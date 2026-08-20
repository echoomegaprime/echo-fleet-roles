from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins/codex/echo-fleet-role-powerpack"
HOOKS = PLUGIN / "hooks"


def load_resolution_module():
    spec = importlib.util.spec_from_file_location("role_resolution", HOOKS / "role_resolution.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class PureRoleResolutionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = load_resolution_module()
        registry = json.loads((PLUGIN / "config/role_power_registry.json").read_text(encoding="utf-8"))
        cls.roles = set(registry["roles"])
        cls.default = registry["default_role"]
        cls.plugin_revision = cls.module.compute_plugin_revision(PLUGIN)

    def receipt(self, **overrides: str):
        values = {
            "role": "builder",
            "child_session_id": "child-17",
            "child_revision": "a" * 40,
            "plugin_revision": self.plugin_revision,
        }
        values.update(overrides)
        return self.module.make_adoption_receipt(**values)

    def resolve(self, **overrides):
        values = {
            "roles": self.roles,
            "default_role": self.default,
            "live_sol_role": None,
            "child_receipt": None,
            "plugin_role": None,
            "child_session_id": "child-17",
            "child_revision": "a" * 40,
            "plugin_revision": self.plugin_revision,
        }
        values.update(overrides)
        return self.module.resolve_role(**values)

    def test_order_is_live_sol_then_bound_child_receipt_then_plugin_then_default(self) -> None:
        receipt = self.receipt()
        live = self.resolve(live_sol_role="judge", child_receipt=receipt, plugin_role="pentester")
        self.assertEqual(("judge", "live_sol"), (live.role, live.source))

        child = self.resolve(child_receipt=receipt, plugin_role="pentester")
        self.assertEqual(("builder", "bound_child_receipt"), (child.role, child.source))

        plugin = self.resolve(plugin_role="pentester")
        self.assertEqual(("pentester", "plugin"), (plugin.role, plugin.source))

        default = self.resolve()
        self.assertEqual((self.default, "default"), (default.role, default.source))

    def test_receipt_is_rejected_unless_child_and_both_revisions_match(self) -> None:
        mutations = (
            {"child_session_id": "sibling"},
            {"child_revision": "b" * 40},
            {"plugin_revision": "sha256:" + "c" * 64},
            {"role": "not-a-role"},
        )
        for mutation in mutations:
            with self.subTest(mutation=mutation):
                decision = self.resolve(child_receipt=self.receipt(**mutation), plugin_role="observer")
                self.assertEqual(("observer", "plugin"), (decision.role, decision.source))

    def test_receipt_is_data_not_a_parent_keyed_temp_state_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            stale = Path(temp) / "echo_active_fleet_role.json"
            stale.write_text(json.dumps({"parent-pid": {"role": "troubleshooter", "loaded": None}}), encoding="utf-8")
            decision = self.resolve(plugin_role="commander")
        self.assertEqual(("commander", "plugin"), (decision.role, decision.source))


class CompatibilityHookTests(unittest.TestCase):
    def run_hook(self, name: str, payload: dict, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(HOOKS / name)],
            input=json.dumps(payload),
            text=True,
            capture_output=True,
            env=env,
            check=False,
        )

    def base_env(self) -> dict[str, str]:
        env = os.environ.copy()
        env["PLUGIN_ROOT"] = str(PLUGIN)
        env.pop("SOL_RUN_ID", None)
        env.pop("SOL_STATE_DB", None)
        return env

    def test_classifier_is_advisory_and_does_not_destroy_loaded_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            state = Path(temp) / "legacy.json"
            original = {"child-17": {"role": "commander", "loaded": "commander", "receipt": "preserve"}}
            state.write_text(json.dumps(original), encoding="utf-8")
            env = self.base_env()
            env["ECHO_ROLE_STATE_FILE"] = str(state)
            result = self.run_hook(
                "delegation_role_advisor.py",
                {"hook_event_name": "UserPromptSubmit", "session_id": "child-17", "prompt": "Debug the broken completion hook."},
                env,
            )

            self.assertEqual(0, result.returncode, result.stderr)
            self.assertEqual(original, json.loads(state.read_text(encoding="utf-8")))
        self.assertIn("advis", result.stdout.casefold())
        self.assertNotIn("mandatory", result.stdout.casefold())
        self.assertNotIn("invoke the skill tool", result.stdout.casefold())

    def test_marker_can_issue_host_neutral_receipt_without_skill_tool(self) -> None:
        module = load_resolution_module()
        with tempfile.TemporaryDirectory() as temp:
            receipt_path = Path(temp) / "adoption.json"
            env = self.base_env()
            env["ECHO_ROLE_ADOPTION_RECEIPT_PATH"] = str(receipt_path)
            result = self.run_hook(
                "role_loaded_marker.py",
                {
                    "hook_event_name": "RoleAdopted",
                    "session_id": "child-17",
                    "role_adoption": {"role": "troubleshooter", "child_revision": "d" * 40},
                },
                env,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
            decision = module.resolve_role(
                roles={"commander", "troubleshooter"},
                default_role="commander",
                live_sol_role=None,
                child_receipt=receipt,
                plugin_role="commander",
                child_session_id="child-17",
                child_revision="d" * 40,
                plugin_revision=module.compute_plugin_revision(PLUGIN),
            )
        self.assertEqual(("troubleshooter", "bound_child_receipt"), (decision.role, decision.source))

    def test_role_context_consumes_the_explicit_receipt_file(self) -> None:
        module = load_resolution_module()
        with tempfile.TemporaryDirectory() as temp:
            receipt_path = Path(temp) / "adoption.json"
            receipt = module.make_adoption_receipt(
                role="troubleshooter",
                child_session_id="child-17",
                child_revision="e" * 40,
                plugin_revision=module.compute_plugin_revision(PLUGIN),
            )
            receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
            env = self.base_env()
            env["ECHO_ROLE_ADOPTION_RECEIPT_PATH"] = str(receipt_path)
            result = self.run_hook(
                "role_context.py",
                {
                    "hook_event_name": "SessionStart",
                    "session_id": "child-17",
                    "child_revision": "e" * 40,
                },
                env,
            )
        self.assertEqual(0, result.returncode, result.stderr)
        context = json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]
        self.assertIn("troubleshooter", context)
        self.assertIn("bound_child_receipt", context)

    def test_gate_does_not_trust_legacy_temp_state(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            state = Path(temp) / "legacy.json"
            state.write_text(json.dumps({"child-17": {"role": "troubleshooter", "loaded": None}}), encoding="utf-8")
            env = self.base_env()
            env["ECHO_ROLE_STATE_FILE"] = str(state)
            result = self.run_hook(
                "role_adoption_gate.py",
                {"hook_event_name": "PreToolUse", "session_id": "child-17", "tool_name": "Bash"},
                env,
            )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertNotIn("deny", result.stdout.casefold())


if __name__ == "__main__":
    unittest.main()
