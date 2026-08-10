"""Create a redacted completion packet from explicit local evidence."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mission", required=True)
    parser.add_argument("--scope", required=True)
    parser.add_argument("--status", choices=("complete", "blocked", "verifying"), required=True)
    parser.add_argument("--tests", nargs="*", default=[])
    parser.add_argument("--files", nargs="*", default=[])
    parser.add_argument("--decision", default="")
    args = parser.parse_args()
    packet = {
        "mission": args.mission,
        "scope": args.scope,
        "status": args.status,
        "tests": args.tests,
        "files": args.files,
        "decision": args.decision,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "redaction": "Inputs are explicit evidence; no secrets or restricted records are read.",
    }
    print(json.dumps(packet, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
