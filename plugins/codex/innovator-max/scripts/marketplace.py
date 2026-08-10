"""Local reviewable catalog for skills, plugins, connectors, and protocols."""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "registry" / "catalog.json"
SUBMISSIONS = ROOT / "registry" / "submissions.json"
PUBLISH_ROLES = {"commander", "deputy_commander", "publisher", "quartermaster"}
MIN_INDEPENDENT_APPROVALS = 2


def read(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def search(query: str) -> list[dict[str, Any]]:
    terms = set(re.findall(r"[a-z0-9][a-z0-9._:-]*", query.lower()))
    entries = read(CATALOG, {"entries": []}).get("entries", [])
    return [
        item for item in entries
        if not terms or terms.intersection(set(re.findall(r"[a-z0-9][a-z0-9._:-]*", json.dumps(item).lower())))
    ]


def submit(args: argparse.Namespace) -> dict[str, Any]:
    data = read(SUBMISSIONS, {"submissions": []})
    item = {"id": args.id, "name": args.name, "kind": args.kind, "source": args.source, "license": args.license, "roles": args.roles, "permissions": args.permissions, "status": "submitted", "submitted_by": args.role, "submitted_at": datetime.now(timezone.utc).isoformat(), "tests": [], "reviews": []}
    data["submissions"] = [old for old in data["submissions"] if old.get("id") != args.id] + [item]
    write(SUBMISSIONS, data)
    return item


def review(args: argparse.Namespace) -> dict[str, Any]:
    data = read(SUBMISSIONS, {"submissions": []})
    for item in data["submissions"]:
        if item.get("id") == args.id:
            if args.role == item.get("submitted_by"):
                raise SystemExit("reviewer_must_differ_from_submitter")
            if any(review.get("reviewer") == args.role for review in item.get("reviews", [])):
                raise SystemExit("one_review_per_role")
            if args.status == "approved" and not args.tests:
                raise SystemExit("approval_requires_executable_test_evidence")
            item["reviews"].append({"reviewer": args.role, "status": args.status, "notes": args.notes, "tests": args.tests, "reviewed_at": datetime.now(timezone.utc).isoformat()})
            if args.status == "rejected":
                item["status"] = "rejected"
            else:
                approved = {review["reviewer"] for review in item["reviews"] if review.get("status") == "approved" and review.get("tests")}
                item["status"] = "approved" if len(approved) >= MIN_INDEPENDENT_APPROVALS else "under-review"
            write(SUBMISSIONS, data)
            return item
    raise SystemExit("submission_not_found")


def publish(args: argparse.Namespace) -> dict[str, Any]:
    data = read(SUBMISSIONS, {"submissions": []})
    match = next((item for item in data["submissions"] if item.get("id") == args.id), None)
    if not match or match.get("status") != "approved":
        raise SystemExit("publish_requires_approved_submission")
    if args.role not in PUBLISH_ROLES:
        raise SystemExit("publisher_role_required")
    participants = {match.get("submitted_by")} | {review.get("reviewer") for review in match.get("reviews", [])}
    if args.role in participants:
        raise SystemExit("publisher_must_be_independent")
    catalog = read(CATALOG, {"entries": []})
    public = {key: value for key, value in match.items() if key not in {"reviews", "submitted_at"}}
    public["status"] = "published"
    public["review_evidence"] = {"independent_approvals": MIN_INDEPENDENT_APPROVALS, "publisher": args.role}
    catalog["entries"] = [old for old in catalog["entries"] if old.get("id") != args.id] + [public]
    write(CATALOG, catalog)
    match["status"] = "published"
    write(SUBMISSIONS, data)
    return public


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="action", required=True)
    find = sub.add_parser("search"); find.add_argument("query", nargs="*", default=[])
    add = sub.add_parser("submit")
    for name in ("id", "name", "kind", "source", "license", "role"):
        add.add_argument("--" + name, required=True)
    add.add_argument("--roles", nargs="*", default=[]); add.add_argument("--permissions", nargs="*", default=[])
    rev = sub.add_parser("review"); rev.add_argument("--id", required=True); rev.add_argument("--role", required=True); rev.add_argument("--status", choices=("approved", "rejected"), required=True); rev.add_argument("--notes", required=True); rev.add_argument("--tests", nargs="*", default=[])
    pub = sub.add_parser("publish"); pub.add_argument("--id", required=True); pub.add_argument("--role", required=True)
    args = parser.parse_args()
    if args.action == "search": result = search(" ".join(args.query))
    elif args.action == "submit": result = submit(args)
    elif args.action == "review": result = review(args)
    else: result = publish(args)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
