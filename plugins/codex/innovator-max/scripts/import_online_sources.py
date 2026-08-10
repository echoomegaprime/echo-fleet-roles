#!/usr/bin/env python3
"""Merge reviewed discovery metadata into the local marketplace catalog."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "registry" / "catalog.json"
SOURCES = ROOT / "registry" / "online_sources.json"


def main() -> int:
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    sources = json.loads(SOURCES.read_text(encoding="utf-8"))["sources"]
    entries = catalog.setdefault("entries", [])
    known = {entry.get("id") for entry in entries}
    for source in sources:
        if source["id"] not in known:
            entries.append({
                **source,
                "roles": ["all"],
                "permissions": ["discovery.read"],
            })
            known.add(source["id"])
    catalog["version"] = "1.4.0"
    CATALOG.write_text(json.dumps(catalog, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"imported": len(sources), "catalog": str(CATALOG), "status": "review-required"}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
