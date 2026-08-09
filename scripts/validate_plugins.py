from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def fail(message: str) -> None:
    raise SystemExit(f"validation failed: {message}")


def main() -> int:
    required_json = [
        ROOT / ".agents/plugins/marketplace.json",
        ROOT / ".claude-plugin/marketplace.json",
        ROOT / "config/role_power_registry.json",
        ROOT / "plugins/codex/echo-fleet-role-powerpack/.codex-plugin/plugin.json",
        ROOT / "plugins/codex/echo-fleet-role-powerpack/hooks/hooks.json",
        ROOT / "plugins/claude-code/echo-fleet-roles/.claude-plugin/plugin.json",
        ROOT / "plugins/claude-code/echo-fleet-roles/hooks/hooks.json",
    ]
    for path in required_json:
        if not path.is_file():
            fail(f"missing {path.relative_to(ROOT)}")
        json.loads(path.read_text(encoding="utf-8"))
    registry = json.loads((ROOT / "config/role_power_registry.json").read_text(encoding="utf-8"))
    if len(registry["roles"]) != 30:
        fail("registry role count is not 30")
    result = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
        cwd=ROOT,
        text=True,
        check=False,
    )
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
