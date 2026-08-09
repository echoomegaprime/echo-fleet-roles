"""Fail-open Codex hook that injects the selected role's context packet."""

from __future__ import annotations

import json
import os
import sqlite3
import sys
from pathlib import Path
from urllib.parse import quote


def state_path() -> Path:
    configured = os.environ.get("ECHO_ROLE_STATE")
    if configured:
        return Path(configured)
    if os.name == "nt":
        root = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
        return root / "EchoFleetRoles" / "state.sqlite3"
    root = Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local" / "state"))
    return root / "echo-fleet-roles" / "state.sqlite3"


def main() -> int:
    try:
        raw_input = sys.stdin.read()
        hook_input = json.loads(raw_input) if raw_input.strip() else {}
        event_name = hook_input.get("hook_event_name", "SessionStart")
        if event_name not in {"SessionStart", "UserPromptSubmit"}:
            event_name = "SessionStart"
        plugin_root = Path(os.environ.get("PLUGIN_ROOT", Path(__file__).resolve().parents[1]))
        registry = json.loads((plugin_root / "config" / "role_power_registry.json").read_text(encoding="utf-8"))
        role_name = registry["default_role"]
        path = state_path()
        if path.exists():
            uri = f"file:{quote(path.resolve().as_posix(), safe='/:')}?mode=ro"
            with sqlite3.connect(uri, uri=True, timeout=2.0) as connection:
                row = connection.execute("SELECT role FROM current_role WHERE singleton=1").fetchone()
                if row and row[0] in registry["roles"]:
                    role_name = row[0]
        role = registry["roles"][role_name]
        context = (
            f"ECHO fleet role selected: {role_name}. Load and follow ${role['primary_skill']}. "
            f"Available composed skills: {', '.join(role['composed_skills'])}. "
            f"Authorized capability families declared by the role: {', '.join(role['capability_families'])}. "
            "Use only tools and authority actually exposed by the current host. Switch roles through echo-role when the objective changes domains; no terminal restart is required."
        )
        print(json.dumps({"hookSpecificOutput": {"hookEventName": event_name, "additionalContext": context}}))
    except Exception:
        # Hooks must never prevent Codex from starting or accepting a prompt.
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
