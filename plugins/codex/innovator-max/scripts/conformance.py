"""Contract tests for plan-first, role-aware, redacted gateway behavior."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from connector_gateway import dispatch  # noqa: E402


def check(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    health = dispatch({"id": "c1", "op": "health"})
    check(health["ok"] and health["connector_count"] >= 6, "health contract")
    doorway = dispatch({"id": "c2", "op": "doorway", "start": str(Path.cwd())})
    check(doorway["ok"] and not doorway["doorway"]["content_included"], "doorway redaction")
    plan = dispatch({"id": "c3", "op": "invoke", "capability": "echo.context.recall", "command": "search", "options": {"query": "x"}})
    check(plan["ok"] and plan["planned"], "plan first")
    denied = dispatch({"id": "c4", "op": "invoke", "capability": "echo.context.recall", "command": "search", "execute": True, "options": {}})
    check(not denied["ok"] and denied["error"] == "policy_denied", "execution role gate")
    unknown = dispatch({"id": "c5", "op": "invoke", "capability": "missing.cap", "command": "x"})
    check(not unknown["ok"], "unknown capability rejection")
    print(json.dumps({"passed": True, "checks": 5}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
