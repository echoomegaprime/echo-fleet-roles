from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class CliTests(unittest.TestCase):
    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["PYTHONPATH"] = str(ROOT / "src")
        return subprocess.run(
            [sys.executable, "-m", "echo_fleet_roles", *args],
            cwd=ROOT,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_validate_command(self) -> None:
        result = self.run_cli("--json", "validate")
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(30, json.loads(result.stdout)["roles"])

    def test_switch_command(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            state = str(Path(temp) / "state.sqlite3")
            result = self.run_cli("--state", state, "--json", "switch", "pentest", "--idempotency-key", "cli-test")
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertEqual("pentester", json.loads(result.stdout)["context"]["role"])

    def test_invalid_role_returns_nonzero(self) -> None:
        result = self.run_cli("--json", "context", "invalid")
        self.assertEqual(2, result.returncode)


if __name__ == "__main__":
    unittest.main()
