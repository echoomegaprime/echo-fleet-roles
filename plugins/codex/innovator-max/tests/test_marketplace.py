from __future__ import annotations

import argparse
import json
import sys
import tempfile
import unittest
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN_ROOT / "scripts"))

import marketplace  # noqa: E402


def ns(**values):
    return argparse.Namespace(**values)


class MarketplaceSeparationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.old_catalog = marketplace.CATALOG
        self.old_submissions = marketplace.SUBMISSIONS
        root = Path(self.temp.name)
        marketplace.CATALOG = root / "catalog.json"
        marketplace.SUBMISSIONS = root / "submissions.json"
        marketplace.write(marketplace.CATALOG, {"entries": []})
        marketplace.write(marketplace.SUBMISSIONS, {"submissions": []})
        marketplace.submit(ns(id="cap-1", name="Cap", kind="skill", source="repo", license="MIT", roles=["all"], permissions=["read"], role="innovator"))

    def tearDown(self) -> None:
        marketplace.CATALOG = self.old_catalog
        marketplace.SUBMISSIONS = self.old_submissions
        self.temp.cleanup()

    def test_two_reviewer_and_independent_publisher_gate(self) -> None:
        with self.assertRaisesRegex(SystemExit, "reviewer_must_differ"):
            marketplace.review(ns(id="cap-1", role="innovator", status="approved", notes="self", tests=["pytest"]))
        first = marketplace.review(ns(id="cap-1", role="beta", status="approved", notes="contract", tests=["pytest -q"]))
        self.assertEqual(first["status"], "under-review")
        second = marketplace.review(ns(id="cap-1", role="quartermaster", status="approved", notes="security", tests=["semgrep --config auto"]))
        self.assertEqual(second["status"], "approved")
        with self.assertRaisesRegex(SystemExit, "publisher_must_be_independent"):
            marketplace.publish(ns(id="cap-1", role="quartermaster"))
        published = marketplace.publish(ns(id="cap-1", role="publisher"))
        self.assertEqual(published["status"], "published")
        self.assertEqual(published["review_evidence"]["independent_approvals"], 2)
        self.assertEqual(json.loads(marketplace.CATALOG.read_text())["entries"][0]["id"], "cap-1")


if __name__ == "__main__":
    unittest.main()
