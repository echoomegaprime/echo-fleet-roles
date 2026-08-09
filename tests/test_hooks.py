from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from echo_fleet_roles.registry import load_registry
from echo_fleet_roles.runtime import RoleRuntime


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins/codex/echo-fleet-role-powerpack"


class HookTests(unittest.TestCase):
    def test_hook_injects_selected_role_for_each_supported_event(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            state = Path(temp) / "roles.sqlite3"
            runtime = RoleRuntime(load_registry(ROOT / "config/role_power_registry.json"), state_path=state)
            runtime.switch("pentester", idempotency_key="hook-test")
            env = os.environ.copy()
            env["PLUGIN_ROOT"] = str(PLUGIN)
            env["ECHO_ROLE_STATE"] = str(state)
            for event in ("SessionStart", "UserPromptSubmit"):
                result = subprocess.run(
                    [sys.executable, str(PLUGIN / "hooks/role_context.py")],
                    input=json.dumps({"hook_event_name": event}),
                    text=True,
                    capture_output=True,
                    env=env,
                    check=False,
                )
                self.assertEqual(0, result.returncode, result.stderr)
                payload = json.loads(result.stdout)
                output = payload["hookSpecificOutput"]
                self.assertEqual(event, output["hookEventName"])
                self.assertIn("pentester", output["additionalContext"])
                self.assertIn("echo-pentester-power", output["additionalContext"])

    def test_hook_fails_open_with_missing_registry(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            env = os.environ.copy()
            env["PLUGIN_ROOT"] = temp
            result = subprocess.run(
                [sys.executable, str(PLUGIN / "hooks/role_context.py")],
                input='{"hook_event_name":"SessionStart"}',
                text=True,
                capture_output=True,
                env=env,
                check=False,
            )
            self.assertEqual(0, result.returncode)
            self.assertEqual("", result.stdout)


if __name__ == "__main__":
    unittest.main()
