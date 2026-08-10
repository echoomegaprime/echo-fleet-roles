"""Standards-compliant MCP surface for the Innovator Max capability gateway.

The FastMCP runtime provides both newline-delimited JSON-RPC stdio and MCP
Streamable HTTP transports. Business logic remains in connector_gateway so all
transports receive the same policy, redaction, retrieval, and audit behavior.
"""
from __future__ import annotations

import argparse
import sys
import uuid
from pathlib import Path
from typing import Any, Literal

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from connector_gateway import dispatch  # noqa: E402


class StrictModel(BaseModel):
    """Reject misspelled fields instead of silently changing intent."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class DoorwayRequest(StrictModel):
    start: str | None = Field(
        default=None,
        description="Optional project path from which to resolve the AGENTS.md/CLAUDE.md doorway chain.",
        max_length=1024,
    )


class RetrievalRequest(StrictModel):
    role: str = Field(description="Fleet role requesting capabilities, for example innovator or builder.", min_length=1, max_length=64)
    intent: str = Field(description="Concrete task or capability intent to match.", min_length=2, max_length=4000)
    sensitivity: Literal["public", "internal", "restricted"] = "internal"
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class MarketplaceRequest(StrictModel):
    query: str = Field(default="", description="Terms to match across catalog metadata.", max_length=1000)
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class InvocationRequest(StrictModel):
    role: str = Field(description="Fleet role used by the execution policy.", min_length=1, max_length=64)
    capability: str = Field(description="Registered echo.* SDK capability.", min_length=3, max_length=255)
    command: str = Field(description="Capability verb; every ECHO SDK call requires it.", min_length=1, max_length=128)
    options: dict[str, Any] = Field(default_factory=dict, description="Capability-specific arguments; never include literal secrets.")
    sensitivity: Literal["public", "internal", "restricted"] = "internal"
    execute: bool = Field(default=False, description="False returns a safe plan. True invokes through the scoped SOL broker if policy permits.")


def _page(items: list[dict[str, Any]], limit: int, offset: int) -> dict[str, Any]:
    selected = items[offset : offset + limit]
    next_offset = offset + len(selected)
    return {
        "total_count": len(items),
        "count": len(selected),
        "offset": offset,
        "items": selected,
        "has_more": next_offset < len(items),
        "next_offset": next_offset if next_offset < len(items) else None,
    }


def create_server(host: str = "127.0.0.1", port: int = 8792) -> FastMCP:
    mcp = FastMCP(
        "innovator_max_mcp",
        instructions=(
            "Discover role-aware ECHO capabilities, resolve the live instruction doorway, "
            "search the reviewed capability marketplace, and invoke only through the shared policy gate."
        ),
        host=host,
        port=port,
        streamable_http_path="/mcp",
        json_response=True,
        stateless_http=True,
    )

    @mcp.tool(
        name="echo_gateway_health",
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
    )
    def gateway_health() -> dict[str, Any]:
        """Return gateway, manifest, connector, role, and provider health metadata."""

        return dispatch({"id": uuid.uuid4().hex, "op": "health"})

    @mcp.tool(
        name="echo_resolve_doorway",
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
    )
    def resolve_doorway(request: DoorwayRequest) -> dict[str, Any]:
        """Resolve the applicable AGENTS.md/CLAUDE.md chain and return hashes/provenance without embedding its full contents."""

        payload: dict[str, Any] = {"id": uuid.uuid4().hex, "op": "doorway"}
        if request.start:
            payload["start"] = request.start
        return dispatch(payload)

    @mcp.tool(
        name="echo_list_roles",
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
    )
    def list_roles() -> dict[str, Any]:
        """List role definitions, global skills, aliases, and the shared connector contract."""

        return dispatch({"id": uuid.uuid4().hex, "op": "roles"})

    @mcp.tool(
        name="echo_retrieve_capabilities",
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
    )
    def retrieve_capabilities(request: RetrievalRequest) -> dict[str, Any]:
        """Rank registered ECHO connectors for a role and intent, with bounded pagination."""

        result = dispatch({"id": uuid.uuid4().hex, "op": "retrieve", **request.model_dump(exclude={"limit", "offset"})})
        if result.get("ok"):
            return {"id": result.get("id"), "ok": True, **_page(result.get("matches", []), request.limit, request.offset)}
        return result

    @mcp.tool(
        name="echo_search_marketplace",
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
    )
    def search_marketplace(request: MarketplaceRequest) -> dict[str, Any]:
        """Search installed, inventory-only, published, and upstream-review-required capabilities."""

        result = dispatch({"id": uuid.uuid4().hex, "op": "marketplace", "action": "search", "query": request.query})
        if result.get("ok"):
            return {"id": result.get("id"), "ok": True, **_page(result.get("entries", []), request.limit, request.offset)}
        return result

    @mcp.tool(
        name="echo_invoke_capability",
        annotations={"readOnlyHint": False, "destructiveHint": True, "idempotentHint": False, "openWorldHint": True},
    )
    def invoke_capability(request: InvocationRequest) -> dict[str, Any]:
        """Plan or explicitly invoke a registered ECHO capability through the role/sensitivity policy and scoped SOL broker."""

        return dispatch({"id": uuid.uuid4().hex, "op": "invoke", **request.model_dump()})

    return mcp


def main() -> int:
    parser = argparse.ArgumentParser(description="Innovator Max MCP server")
    parser.add_argument("--transport", choices=("stdio", "streamable-http"), default="stdio")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8792)
    args = parser.parse_args()
    if args.transport == "streamable-http" and args.host not in {"127.0.0.1", "localhost", "::1"}:
        raise SystemExit("Streamable HTTP is intentionally loopback-only; use provider_server.py for authenticated remote clients.")
    create_server(args.host, args.port).run(transport=args.transport)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
