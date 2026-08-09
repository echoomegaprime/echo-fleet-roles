from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from echo_fleet_roles.registry import load_registry
from echo_fleet_roles.runtime import RoleRuntime
from echo_fleet_roles.state import StateConflict


ROOT = Path(__file__).resolve().parents[1]


class StateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.state = Path(self.temp.name) / "roles.sqlite3"
        self.runtime = RoleRuntime(
            load_registry(ROOT / "config" / "role_power_registry.json"), state_path=self.state
        )

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_default_role_is_commander(self) -> None:
        self.assertEqual("commander", self.runtime.current()["role"])

    def test_switch_is_immediate_and_persistent(self) -> None:
        result = self.runtime.switch("z", expected_current="c", idempotency_key="phase-re")
        self.assertTrue(result["transition"]["changed"])
        self.assertEqual("reverse-engineer", self.runtime.current()["role"])
        self.assertFalse(result["context"]["requires_new_session"])

    def test_idempotency_replays_original_transition(self) -> None:
        first = self.runtime.switch("builder", idempotency_key="same-request")
        replay = self.runtime.switch("builder", idempotency_key="same-request")
        self.assertEqual(first["transition"], replay["transition"])
        self.assertEqual("builder", self.runtime.current()["role"])

    def test_idempotency_key_cannot_be_reused_for_different_role(self) -> None:
        self.runtime.switch("builder", idempotency_key="same-request")
        with self.assertRaises(StateConflict):
            self.runtime.switch("pentester", idempotency_key="same-request")
        self.assertEqual("builder", self.runtime.current()["role"])

    def test_expected_current_fences_concurrent_change(self) -> None:
        self.runtime.switch("builder")
        with self.assertRaises(StateConflict):
            self.runtime.switch("publisher", expected_current="commander")
        self.assertEqual("builder", self.runtime.current()["role"])

    def test_same_role_is_audited_noop(self) -> None:
        result = self.runtime.switch("commander", idempotency_key="noop")
        self.assertFalse(result["transition"]["changed"])
        self.assertEqual(1, len(self.runtime.state.history()))


if __name__ == "__main__":
    unittest.main()
