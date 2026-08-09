"""Claude Code compatibility copy of the fail-open ECHO role hook."""

from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path
from urllib.parse import quote


def main() -> int:
    try:
        root = Path(os.environ.get("CLAUDE_PLUGIN_ROOT", Path(__file__).resolve().parents[1]))
        registry = json.loads((root / "config" / "role_power_registry.json").read_text(encoding="utf-8"))
        if os.name == "nt":
            state = Path(os.environ.get("ECHO_ROLE_STATE", Path(os.environ.get("LOCALAPPDATA", Path.home())) / "EchoFleetRoles" / "state.sqlite3"))
        else:
            state = Path(os.environ.get("ECHO_ROLE_STATE", Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local" / "state")) / "echo-fleet-roles" / "state.sqlite3"))
        role_name = registry["default_role"]
        if state.exists():
            uri = f"file:{quote(state.resolve().as_posix(), safe='/:')}?mode=ro"
            with sqlite3.connect(uri, uri=True, timeout=2.0) as connection:
                row = connection.execute("SELECT role FROM current_role WHERE singleton=1").fetchone()
                if row and row[0] in registry["roles"]:
                    role_name = row[0]
        role = registry["roles"][role_name]
        print(f"ECHO fleet role selected: {role_name}. Load and follow ${role['primary_skill']}. Same-session switching is available through echo-role. Use only host-authorized tools and scopes.")
    except Exception:
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
