"""Resolve an instruction doorway without emitting document contents."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def ancestors(start: Path) -> list[Path]:
    current = start.resolve()
    if current.is_file():
        current = current.parent
    chain = list(current.parents)
    chain.append(current)
    return sorted(set(chain), key=lambda path: len(path.parts))


def manifest(start: Path) -> dict:
    records = []
    for directory in ancestors(start):
        for filename in ("AGENTS.md", "CLAUDE.md"):
            path = directory / filename
            if not path.is_file():
                continue
            data = path.read_bytes()
            records.append({
                "path": str(path),
                "name": filename,
                "priority": len(records),
                "bytes": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
            })
    pointers = []
    for relative in ("DOORWAY_EXPLAINED.md", "config/scopes.yaml", "indexes/SOURCE_INDEX.md", "indexes/QUICK_LOAD_MAP.md"):
        path = start.resolve() / relative
        if path.is_file():
            pointers.append({"path": str(path), "kind": "pointer"})
    return {
        "start": str(start.resolve()),
        "load_order": "user → overlay → nearest AGENTS/CLAUDE → root router → scoped modules",
        "instruction_files": records,
        "pointers": pointers,
        "tiers": {
            "T1": "doorway doctrine and retrieval bootstrap",
            "T2": "session-start auto-injection",
            "T3": "on-demand live knowledge and scoped modules",
            "T4": "deep storage and fallback mirrors",
        },
        "live_truth_rule": "retrieve moving facts through the live system; do not trust stale summaries",
        "instrument_verification": "verify the retrieval instrument before believing its result",
        "content_included": False,
        "redaction": "Document contents are intentionally omitted from this manifest.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", default=".")
    args = parser.parse_args()
    print(json.dumps(manifest(Path(args.start)), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
