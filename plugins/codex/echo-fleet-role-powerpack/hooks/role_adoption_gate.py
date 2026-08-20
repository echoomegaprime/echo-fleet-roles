"""Gate only an explicit governed role requirement; ignore legacy classifier state."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from role_context import _live_sol_role, _read_role, state_path
from role_resolution import compute_plugin_revision, resolve_role


def _read_optional_receipt(payload: dict[str, object]) -> object:
    direct = payload.get("role_adoption_receipt")
    if direct is not None:
        return direct
    path_value = os.environ.get("ECHO_ROLE_ADOPTION_RECEIPT_PATH", "").strip()
    if not path_value:
        return None
    try:
        return json.loads(Path(path_value).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def main() -> int:
    try:
        payload = json.loads(sys.stdin.read() or "{}")
        required_role = str(payload.get("required_role") or "").strip()
        if not required_role:
            return 0
        plugin_root = Path(os.environ.get("PLUGIN_ROOT", Path(__file__).resolve().parents[1]))
        registry = json.loads((plugin_root / "config" / "role_power_registry.json").read_text(encoding="utf-8"))
        roles = set(registry["roles"])
        if required_role not in roles:
            return 0
        decision = resolve_role(
            roles=roles,
            default_role=str(registry["default_role"]),
            live_sol_role=_live_sol_role(),
            child_receipt=_read_optional_receipt(payload),
            plugin_role=_read_role(state_path(), "SELECT role FROM current_role WHERE singleton=1", ()),
            child_session_id=str(payload.get("session_id") or "") or None,
            child_revision=str(payload.get("child_revision") or "") or None,
            plugin_revision=compute_plugin_revision(plugin_root),
        )
        if decision.role != required_role:
            reason = (
                f"Governed role adoption is incomplete: required={required_role}, resolved={decision.role} "
                f"from {decision.source}. Complete the same-session role transition and provide its bound receipt."
            )
            print(json.dumps({"hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": reason,
            }}))
    except Exception:
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
