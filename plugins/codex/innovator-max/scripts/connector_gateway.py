"""Provider-neutral JSONL gateway for CLIs, chats, MCP bridges, and SDK clients.

Protocol requests are one JSON object per line. Responses are one JSON object per line.
The gateway is intentionally small: clients share discovery and policy while providers
remain replaceable. No shell parsing or credential lookup occurs here.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from connector_runtime import load, redact, retrieve, guarded_invoke
from security import verify_manifest
from marketplace import search as marketplace_search, submit as marketplace_submit, review as marketplace_review, publish as marketplace_publish

PLUGIN_ROOT = Path(__file__).resolve().parents[1]


def _resolve_repo_root() -> Path:
    """Find the ECHO checkout even when this plugin runs from an installed cache."""
    marker = Path("SYSTEMS") / "codex_auto" / "sol_cli.py"
    here = Path(__file__).resolve()
    cwd = Path.cwd().resolve()
    candidates = (cwd, *cwd.parents, *here.parents, Path("C:/ECHO_OMEGA_PRIME"))
    return next((path for path in candidates if (path / marker).is_file()), here.parents[3])


REPO_ROOT = _resolve_repo_root()
sys.path.insert(0, str(PLUGIN_ROOT / "skills" / "doorway-integration" / "scripts"))
try:
    from doorway_loader import manifest as doorway_manifest  # noqa: E402
except ImportError:
    # Deliberately soft, unlike the `security` import in connector_runtime.
    # `security` is the authorization boundary: losing it must stop the process,
    # because continuing without it means executing unchecked. `doorway_loader`
    # backs exactly one optional read-only op, and a hard import meant the whole
    # bridge -- health, list, retrieve, invoke -- died at import time in any tree
    # that does not ship the doorway-integration skill. The deployed capability
    # tree is one such tree, so `--stdio` had never started there at all.
    doorway_manifest = None  # type: ignore[assignment]


def providers() -> list[dict[str, Any]]:
    path = PLUGIN_ROOT / "registry" / "providers.json"
    return json.loads(path.read_text(encoding="utf-8")).get("providers", [])


def roles() -> dict[str, Any]:
    path = PLUGIN_ROOT / "registry" / "roles.json"
    return json.loads(path.read_text(encoding="utf-8"))


def manifest_status() -> dict[str, Any]:
    path = PLUGIN_ROOT / "registry" / "manifest.json"
    if not path.is_file():
        return {"present": False, "verified": False, "required": False, "reason": "manifest not built"}
    return {"present": True, **verify_manifest(json.loads(path.read_text(encoding="utf-8")))}


def dispatch(request: dict[str, Any]) -> dict[str, Any]:
    request_id = request.get("id")
    operation = request.get("op", "health")
    if operation == "health":
        return {"id": request_id, "ok": True, "providers": providers(), "role_count": len(roles().get("roles", [])), "connector_count": len(load()), "manifest": manifest_status(), "instrument_verified": True}
    if operation == "list":
        return {"id": request_id, "ok": True, "connectors": [item.__dict__ for item in load()]}
    if operation == "roles":
        return {"id": request_id, "ok": True, **roles()}
    if operation == "doorway":
        if doorway_manifest is None:
            return {"id": request_id, "ok": False, "error": "doorway_unavailable",
                    "detail": "the doorway-integration skill is not present in this tree"}
        return {"id": request_id, "ok": True, "doorway": doorway_manifest(Path(request.get("start", REPO_ROOT)))}
    if operation == "marketplace":
        action = request.get("action", "search")
        if action == "search":
            return {"id": request_id, "ok": True, "entries": marketplace_search(request.get("query", ""))}
        if not request.get("role"):
            return {"id": request_id, "ok": False, "error": "role_required"}
        args = argparse.Namespace(**request)
        if action == "submit": result = marketplace_submit(args)
        elif action == "review": result = marketplace_review(args)
        elif action == "publish": result = marketplace_publish(args)
        else: return {"id": request_id, "ok": False, "error": "unknown_marketplace_action"}
        return {"id": request_id, "ok": True, "result": result}
    if operation == "retrieve":
        required = ("role", "intent")
        missing = [key for key in required if not request.get(key)]
        if missing:
            return {"id": request_id, "ok": False, "error": "missing_fields", "fields": missing}
        return {"id": request_id, "ok": True, "matches": retrieve(request["role"], request["intent"], request.get("sensitivity", "internal"))}
    if operation == "invoke":
        # Delegates to the shared boundary in connector_runtime rather than keeping
        # a second copy of policy/allowlist/plan-default/audit here. The CLI client
        # previously had no copy at all, which is exactly how a duplicated boundary
        # fails: the weakest client becomes the way in.
        return guarded_invoke(request)
    return {"id": request_id, "ok": False, "error": "unknown_operation", "supported": ["doorway", "health", "list", "roles", "marketplace", "retrieve", "invoke"]}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stdio", action="store_true", help="read JSONL requests from stdin")
    parser.add_argument("--request", help="process one JSON request")
    args = parser.parse_args()
    if args.request:
        print(json.dumps(redact(dispatch(json.loads(args.request))), sort_keys=True))
        return 0
    if not args.stdio:
        parser.error("use --stdio or --request")
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            response = dispatch(json.loads(line))
        except (json.JSONDecodeError, TypeError, ValueError) as exc:
            response = {"ok": False, "error": "invalid_request", "detail": str(exc)}
        print(json.dumps(redact(response), separators=(",", ":")), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
