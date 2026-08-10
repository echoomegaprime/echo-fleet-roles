"""Authenticated A2A v1.0 and OpenAI-compatible adapters for Innovator Max."""
from __future__ import annotations

import argparse
import hmac
import json
import os
import sys
import time
import uuid
from collections import defaultdict, deque
from pathlib import Path
from typing import Any

import uvicorn
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.routes import create_agent_card_routes, create_jsonrpc_routes
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentInterface,
    AgentProvider,
    AgentSkill,
    HTTPAuthSecurityScheme,
    Message,
    Part,
    Role,
    SecurityRequirement,
    SecurityScheme,
    StringList,
)
from a2a.utils.errors import UnsupportedOperationError
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from connector_gateway import dispatch  # noqa: E402
from connector_runtime import redact  # noqa: E402

MAX_BODY_BYTES = 1_048_576


def _extract_text(messages: list[dict[str, Any]]) -> str:
    for message in reversed(messages):
        if message.get("role") != "user":
            continue
        content = message.get("content", "")
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            return "\n".join(
                str(part.get("text", "")) for part in content
                if isinstance(part, dict) and part.get("type") in {"text", "input_text"}
            )
    return ""


def _gateway_request(text: str, role: str = "innovator") -> dict[str, Any]:
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        parsed = None
    if isinstance(parsed, dict) and parsed.get("op"):
        parsed.setdefault("id", uuid.uuid4().hex)
        parsed.setdefault("role", role)
        return parsed
    return {"id": uuid.uuid4().hex, "op": "retrieve", "role": role, "intent": text or "gateway health"}


class GatewayAgentExecutor(AgentExecutor):
    """Expose the shared role-aware dispatcher as an A2A agent."""

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        request = _gateway_request(context.get_user_input())
        result = redact(dispatch(request))
        message = Message(
            message_id=uuid.uuid4().hex,
            context_id=context.context_id or "",
            task_id=context.task_id or "",
            role=Role.ROLE_AGENT,
            parts=[Part(text=json.dumps(result, sort_keys=True, separators=(",", ":")))],
        )
        await event_queue.enqueue_event(message)

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        del context, event_queue
        raise UnsupportedOperationError(message="Immediate gateway responses do not create cancellable tasks.")


def _agent_card(base_url: str) -> AgentCard:
    bearer = SecurityScheme(
        http_auth_security_scheme=HTTPAuthSecurityScheme(
            scheme="bearer",
            bearer_format="opaque",
            description="Token from the ECHO_CONNECTOR_HTTP_TOKEN environment boundary.",
        )
    )
    return AgentCard(
        name="ECHO Innovator Max Capability Agent",
        description="Role-aware discovery, doorway resolution, marketplace search, and policy-gated ECHO capability invocation.",
        supported_interfaces=[AgentInterface(url=f"{base_url.rstrip('/')}/a2a", protocol_binding="JSONRPC", protocol_version="1.0")],
        provider=AgentProvider(organization="ECHO OMEGA PRIME", url="https://echo-op.com"),
        version="0.2.0",
        capabilities=AgentCapabilities(streaming=False, push_notifications=False, extended_agent_card=False),
        security_schemes={"bearer": bearer},
        security_requirements=[SecurityRequirement(schemes={"bearer": StringList(list=[])})],
        default_input_modes=["text/plain", "application/json"],
        default_output_modes=["application/json", "text/plain"],
        skills=[
            AgentSkill(
                id="echo-capability-routing",
                name="ECHO Capability Routing",
                description="Resolve role-appropriate tools and submit policy-gated plan or invocation requests.",
                tags=["echo", "skills", "connectors", "roles", "sdk"],
                examples=["Find the best approved graphics capability for the innovator role."],
                input_modes=["text/plain", "application/json"],
                output_modes=["application/json"],
            )
        ],
    )


def create_app(token: str, base_url: str, allowed_origins: set[str] | None = None, rate_limit_per_minute: int = 120) -> FastAPI:
    if not token:
        raise ValueError("A non-empty bearer token is required.")
    app = FastAPI(title="Innovator Max Provider Gateway", version="0.2.0")
    allowed_origins = allowed_origins or set()
    calls: dict[str, deque[float]] = defaultdict(deque)

    @app.middleware("http")
    async def security_boundary(request: Request, call_next):
        origin = request.headers.get("origin")
        if origin and origin not in allowed_origins:
            return JSONResponse({"ok": False, "error": "origin_denied"}, status_code=403)
        if request.url.path not in {"/health", "/.well-known/agent-card.json"}:
            supplied = request.headers.get("authorization", "")
            if not hmac.compare_digest(supplied, "Bearer " + token):
                return JSONResponse({"ok": False, "error": "unauthorized"}, status_code=401)
            client = request.client.host if request.client else "unknown"
            now = time.monotonic()
            window = calls[client]
            while window and now - window[0] >= 60:
                window.popleft()
            if len(window) >= rate_limit_per_minute:
                return JSONResponse({"ok": False, "error": "rate_limited"}, status_code=429, headers={"Retry-After": "60"})
            window.append(now)
        if request.url.path == "/a2a" and request.headers.get("a2a-version") != "1.0":
            return JSONResponse({"ok": False, "error": "unsupported_a2a_version"}, status_code=400)
        content_length = int(request.headers.get("content-length", "0") or "0")
        if content_length > MAX_BODY_BYTES:
            return JSONResponse({"ok": False, "error": "request_too_large"}, status_code=413)
        response = await call_next(request)
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        return response

    @app.get("/health")
    async def health() -> dict[str, Any]:
        return {"service": "innovator-max-provider-gateway", "status": "ok", "protocols": ["a2a-1.0-jsonrpc", "openai-chat-completions", "echo-json"]}

    @app.get("/v1/models")
    async def models() -> dict[str, Any]:
        return {"object": "list", "data": [{"id": "echo-capability-gateway", "object": "model", "owned_by": "echo-omega-prime"}]}

    @app.post("/v1/connector")
    async def connector(request: Request) -> JSONResponse:
        body = await request.json()
        result = redact(dispatch(body))
        return JSONResponse(result, status_code=200 if result.get("ok") else 400)

    @app.post("/v1/chat/completions")
    async def chat_completions(request: Request):
        body = await request.json()
        text = _extract_text(body.get("messages", []))
        role = str(body.get("echo", {}).get("role", "innovator")) if isinstance(body.get("echo"), dict) else "innovator"
        result_text = json.dumps(redact(dispatch(_gateway_request(text, role))), sort_keys=True, separators=(",", ":"))
        completion_id = "chatcmpl-" + uuid.uuid4().hex
        created = int(time.time())
        if body.get("stream"):
            async def chunks():
                first = {"id": completion_id, "object": "chat.completion.chunk", "created": created, "model": "echo-capability-gateway", "choices": [{"index": 0, "delta": {"role": "assistant", "content": result_text}, "finish_reason": None}]}
                last = {"id": completion_id, "object": "chat.completion.chunk", "created": created, "model": "echo-capability-gateway", "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}]}
                yield "data: " + json.dumps(first, separators=(",", ":")) + "\n\n"
                yield "data: " + json.dumps(last, separators=(",", ":")) + "\n\n"
                yield "data: [DONE]\n\n"
            return StreamingResponse(chunks(), media_type="text/event-stream")
        return {
            "id": completion_id,
            "object": "chat.completion",
            "created": created,
            "model": "echo-capability-gateway",
            "choices": [{"index": 0, "message": {"role": "assistant", "content": result_text}, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
        }

    card = _agent_card(base_url)
    handler = DefaultRequestHandler(GatewayAgentExecutor(), InMemoryTaskStore(), card)
    # Mount the official SDK's Starlette routes directly. Its optional FastAPI
    # OpenAPI enricher currently assumes Protobuf 6-only descriptor helpers;
    # direct mounting keeps the wire implementation official-SDK backed while
    # preserving compatibility with the broader fleet's Protobuf 5 consumers.
    app.router.routes.extend(create_agent_card_routes(card))
    app.router.routes.extend(create_jsonrpc_routes(handler, rpc_url="/a2a"))
    return app


def main() -> int:
    parser = argparse.ArgumentParser(description="Authenticated A2A and OpenAI-compatible Innovator Max gateway")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8791)
    parser.add_argument("--base-url", default=None)
    parser.add_argument("--rate-limit", type=int, default=120)
    parser.add_argument("--allow-origin", action="append", default=[])
    parser.add_argument("--allow-unauthenticated-local", action="store_true")
    args = parser.parse_args()
    token = os.environ.get("ECHO_CONNECTOR_HTTP_TOKEN", "")
    if not token:
        if not args.allow_unauthenticated_local or args.host not in {"127.0.0.1", "localhost", "::1"}:
            raise SystemExit("ECHO_CONNECTOR_HTTP_TOKEN is required (or use the explicit localhost-only development override).")
        token = uuid.uuid4().hex
    base_url = args.base_url or f"http://{args.host}:{args.port}"
    uvicorn.run(create_app(token, base_url, set(args.allow_origin), args.rate_limit), host=args.host, port=args.port, log_level="info")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
