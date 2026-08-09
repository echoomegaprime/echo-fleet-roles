from __future__ import annotations

import json
import re
from collections import Counter
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ROLE_SKILLS = {
    "echo-architect-power", "echo-beta-power", "echo-builder-power", "echo-cli-build-power",
    "echo-commander-power", "echo-compliance-officer-power", "echo-curator-power",
    "echo-data-engineer-power", "echo-deputy-commander-power", "echo-enhancer-power",
    "echo-experience-designer-power", "echo-harbormaster-power", "echo-innovator-power",
    "echo-judge-power", "echo-landman-power", "echo-marketing-power", "echo-observer-power",
    "echo-osint-power", "echo-pentester-power", "echo-prime-power", "echo-product-manager-power",
    "echo-publisher-power", "echo-quartermaster-power", "echo-researcher-power",
    "echo-reverse-engineering", "echo-sentinel-power", "echo-steward-power",
    "echo-surveyor-power", "echo-trainer-power", "echo-troubleshooter-power",
}


class PackagingTests(unittest.TestCase):
    def test_both_hosts_have_all_roles_and_switching_skill(self) -> None:
        for relative in ("plugins/codex/echo-fleet-role-powerpack", "plugins/claude-code/echo-fleet-roles"):
            skills = {path.name for path in (ROOT / relative / "skills").iterdir() if path.is_dir()}
            self.assertEqual(ROLE_SKILLS | {"echo-role-switching"}, skills)

    def test_skill_frontmatter_matches_directory(self) -> None:
        for skill_file in ROOT.glob("plugins/*/*/skills/*/SKILL.md"):
            text = skill_file.read_text(encoding="utf-8")
            match = re.match(r"---\s*\nname:\s*([^\n]+)\ndescription:\s*([^\n]+)\n---", text)
            self.assertIsNotNone(match, str(skill_file))
            self.assertEqual(skill_file.parent.name, match.group(1).strip())
            self.assertGreaterEqual(len(match.group(2).strip()), 40)

    def test_marketplace_paths_resolve(self) -> None:
        codex = json.loads((ROOT / ".agents/plugins/marketplace.json").read_text(encoding="utf-8"))
        for plugin in codex["plugins"]:
            path = plugin["source"]["path"]
            self.assertTrue(path.startswith("./"))
            self.assertTrue((ROOT / path[2:]).is_dir())
        claude = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text(encoding="utf-8"))
        for plugin in claude["plugins"]:
            self.assertTrue((ROOT / plugin["source"][2:]).is_dir())

    def test_no_private_infrastructure_literals(self) -> None:
        forbidden = [r"192\.168\.1\.", r"100\.\d+\.\d+\.\d+", r"C:\\ECHO_OMEGA_PRIME", r"/home/forge", r"master_vault\.db"]
        for path in ROOT.glob("plugins/**/*"):
            if path.is_file() and path.suffix.lower() in {".md", ".json", ".py"}:
                text = path.read_text(encoding="utf-8", errors="replace")
                for pattern in forbidden:
                    self.assertIsNone(re.search(pattern, text, re.IGNORECASE), f"{pattern} in {path}")

    def test_golden_prompt_contract(self) -> None:
        payload = json.loads((ROOT / "evals/golden-prompts.json").read_text(encoding="utf-8"))
        cases = payload["cases"]
        self.assertEqual(60, len(cases))
        self.assertEqual(
            {"direct": 10, "indirect": 10, "ambiguous": 10, "negative": 10,
             "malformed": 5, "unauthorized": 5, "destructive": 5, "injection": 5},
            dict(Counter(case["category"] for case in cases)),
        )
        registry = json.loads((ROOT / "config/role_power_registry.json").read_text(encoding="utf-8"))
        for case in cases:
            if case["should_activate"]:
                self.assertIn(case["expected_role"], registry["roles"], case["id"])
            else:
                self.assertIsNone(case["expected_role"], case["id"])


if __name__ == "__main__":
    unittest.main()
