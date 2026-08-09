from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from echo_fleet_roles.registry import RegistryError, load_registry, parse_registry


ROOT = Path(__file__).resolve().parents[1]


class RegistryTests(unittest.TestCase):
    def test_registry_has_exactly_thirty_roles(self) -> None:
        registry = load_registry(ROOT / "config" / "role_power_registry.json")
        self.assertEqual(30, len(registry.roles))
        self.assertEqual("commander", registry.default_role)

    def test_required_specialists_are_first_class_roles(self) -> None:
        registry = load_registry(ROOT / "config" / "role_power_registry.json")
        self.assertEqual("echo-reverse-engineering", registry.role("z").primary_skill)
        self.assertEqual("echo-pentester-power", registry.role("pentest").primary_skill)
        self.assertEqual("echo-compliance-officer-power", registry.role("compliance").primary_skill)

    def test_registry_contains_no_private_boot_paths_or_plugin_override(self) -> None:
        raw = json.loads((ROOT / "config" / "role_power_registry.json").read_text(encoding="utf-8"))
        for role in raw["roles"].values():
            self.assertNotIn("boot_prompt", role)
            self.assertNotIn("plugin", role)

    def test_unknown_role_is_rejected(self) -> None:
        registry = load_registry(ROOT / "config" / "role_power_registry.json")
        with self.assertRaises(RegistryError):
            registry.resolve("not-a-role")

    def test_extra_role_fields_are_rejected(self) -> None:
        payload = json.loads((ROOT / "config" / "role_power_registry.json").read_text(encoding="utf-8"))
        payload["roles"]["commander"]["unsafe_extra"] = True
        with self.assertRaises(RegistryError):
            parse_registry(payload)


if __name__ == "__main__":
    unittest.main()
