from __future__ import annotations

import json
import os
import sqlite3
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
            env.pop("SOL_RUN_ID", None)
            env.pop("SOL_STATE_DB", None)
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

    def test_hook_prefers_live_sol_role_over_stale_plugin_role(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            temp_root = Path(temp)
            role_state = temp_root / "roles.sqlite3"
            runtime = RoleRuntime(load_registry(ROOT / "config/role_power_registry.json"), state_path=role_state)
            runtime.switch("pentester", idempotency_key="stale-role")

            sol_state = temp_root / "sol.sqlite3"
            connection = sqlite3.connect(sol_state)
            try:
                connection.execute("CREATE TABLE missions (run_id TEXT PRIMARY KEY, role TEXT NOT NULL)")
                connection.execute(
                    "INSERT INTO missions(run_id, role) VALUES (?, ?)",
                    ("sol-hook-test", "cli-build"),
                )
                connection.commit()
            finally:
                connection.close()

            env = os.environ.copy()
            env["PLUGIN_ROOT"] = str(PLUGIN)
            env["ECHO_ROLE_STATE"] = str(role_state)
            env["SOL_STATE_DB"] = str(sol_state)
            env["SOL_RUN_ID"] = "sol-hook-test"
            result = subprocess.run(
                [sys.executable, str(PLUGIN / "hooks/role_context.py")],
                input=json.dumps({"hook_event_name": "SessionStart"}),
                text=True,
                capture_output=True,
                env=env,
                check=False,
            )

            self.assertEqual(0, result.returncode, result.stderr)
            context = json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]
            self.assertIn("cli-build", context)
            self.assertIn("echo-cli-build-power", context)
            self.assertNotIn("ECHO fleet role selected: pentester", context)

    def test_user_prompt_explicit_role_is_pinned(self) -> None:
        env = os.environ.copy()
        env["PLUGIN_ROOT"] = str(PLUGIN)
        env.pop("SOL_RUN_ID", None)
        env.pop("SOL_STATE_DB", None)
        with tempfile.TemporaryDirectory() as temp:
            role_state = Path(temp) / "roles.sqlite3"
            runtime = RoleRuntime(load_registry(ROOT / "config/role_power_registry.json"), state_path=role_state)
            runtime.switch("pentester", idempotency_key="explicit-role-mismatch")
            env["ECHO_ROLE_STATE"] = str(role_state)
            result = subprocess.run(
                [sys.executable, str(PLUGIN / "hooks/role_context.py")],
                input=json.dumps(
                    {
                        "hook_event_name": "UserPromptSubmit",
                        "prompt": "Start this ECHO Codex session as the 'commander' fleet role.",
                    }
                ),
                text=True,
                capture_output=True,
                env=env,
                check=False,
            )

        self.assertEqual(0, result.returncode, result.stderr)
        context = json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]
        self.assertIn("Explicit role directive: commander", context)
        self.assertIn("pinned", context.lower())
        self.assertIn("switch before acting", context.lower())

    def test_user_prompt_without_explicit_role_emits_selection_gate(self) -> None:
        env = os.environ.copy()
        env["PLUGIN_ROOT"] = str(PLUGIN)
        env.pop("SOL_RUN_ID", None)
        env.pop("SOL_STATE_DB", None)
        with tempfile.TemporaryDirectory() as temp:
            env["ECHO_ROLE_STATE"] = str(Path(temp) / "missing.sqlite3")
            result = subprocess.run(
                [sys.executable, str(PLUGIN / "hooks/role_context.py")],
                input=json.dumps(
                    {
                        "hook_event_name": "UserPromptSubmit",
                        "prompt": "Add debug logging to the worker and verify the fix.",
                    }
                ),
                text=True,
                capture_output=True,
                env=env,
                check=False,
            )

        self.assertEqual(0, result.returncode, result.stderr)
        context = json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]
        self.assertIn("Role selection gate", context)
        self.assertIn("same-session role switch", context)

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
