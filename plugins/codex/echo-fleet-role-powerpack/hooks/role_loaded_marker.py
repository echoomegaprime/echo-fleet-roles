"""Issue a revision-bound adoption receipt without depending on a host Skill tool."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from role_resolution import compute_plugin_revision, make_adoption_receipt


def main() -> int:
    try:
        payload = json.loads(sys.stdin.read() or "{}")
        adoption = payload.get("role_adoption")
        if not isinstance(adoption, dict):
            return 0
        session_id = str(payload.get("session_id") or "").strip()
        role = str(adoption.get("role") or "").strip()
        child_revision = str(adoption.get("child_revision") or "").strip()
        receipt_path = os.environ.get("ECHO_ROLE_ADOPTION_RECEIPT_PATH", "").strip()
        if not session_id or not role or not child_revision or not receipt_path:
            return 0
        plugin_root = Path(os.environ.get("PLUGIN_ROOT", Path(__file__).resolve().parents[1]))
        registry = json.loads((plugin_root / "config" / "role_power_registry.json").read_text(encoding="utf-8"))
        if role not in registry["roles"]:
            return 0
        receipt = make_adoption_receipt(
            role=role,
            child_session_id=session_id,
            child_revision=child_revision,
            plugin_revision=compute_plugin_revision(plugin_root),
        )
        destination = Path(receipt_path).resolve()
        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary = destination.with_name(destination.name + f".{os.getpid()}.tmp")
        temporary.write_text(json.dumps(receipt, sort_keys=True), encoding="utf-8")
        os.replace(temporary, destination)
    except Exception:
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
