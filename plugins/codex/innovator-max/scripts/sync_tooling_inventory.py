#!/usr/bin/env python3
"""Import named surfaces and live counts from TOOLING_INVENTORY.md.

The markdown remains the source document. This creates a searchable catalog
projection and never promotes presence to trust or execution permission.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]
PLUGIN_ROOT = REPO_ROOT / "plugins" / "innovator-max"
SOURCE = REPO_ROOT / "TOOLING_INVENTORY.md"
OUT = PLUGIN_ROOT / "registry" / "tooling_inventory.json"
CATALOG = PLUGIN_ROOT / "registry" / "catalog.json"


def section(text: str, heading: str, next_heading: str | None = None) -> str:
    start = text.find(heading)
    if start < 0:
        return ""
    body = text[start + len(heading):]
    if next_heading:
        end = body.find(next_heading)
        if end >= 0:
            body = body[:end]
    return body


def named_tokens(text: str) -> list[str]:
    return sorted(set(re.findall(r"`([A-Za-z0-9][A-Za-z0-9_.-]*)`", text)))


def surface(kind: str, name: str, source: str, provider: str = "claude-echo-inventory") -> dict[str, Any]:
    return {
        "id": f"inventory:{kind}:{name}",
        "name": name,
        "kind": kind,
        "provider": provider,
        "source": source,
        "status": "inventory-only-review-required",
        "roles": ["all"],
        "permissions": ["discovery.read"],
    }


def main() -> int:
    text = SOURCE.read_text(encoding="utf-8", errors="replace")
    counts: dict[str, int] = {}
    for row in re.findall(r"\|\s*([^|]+?)\s*\|\s*`?([^|]+?)`?\s*\|\s*\*\*(\d+)\*\*", text):
        counts[row[0].strip()] = int(row[2])

    surfaces: list[dict[str, Any]] = []
    mcp = section(text, "## 1. MCP SERVERS", "## 2. ECHO PLUGINS")
    for name in re.findall(r"\|\s*\*\*([^*]+)\*\*\s*\|", mcp):
        surfaces.append(surface("mcp", name.strip(), str(SOURCE)))

    echo_plugins = section(text, "## 2. ECHO PLUGINS", "## 3. OFFICIAL PLUGINS")
    for name in re.findall(r"\|\s*\*\*([^*]+)\*\*\s*\|", echo_plugins):
        surfaces.append(surface("plugin", name.strip(), str(SOURCE), "echo-omega-prime"))

    official = section(text, "## 3. OFFICIAL PLUGINS", "## 4. USER SKILLS")
    for name in named_tokens(official):
        surfaces.append(surface("plugin", name, str(SOURCE), "claude-official"))

    user_skills = section(text, "## 4. USER SKILLS", "## 5. SLASH COMMANDS")
    for name in named_tokens(user_skills):
        surfaces.append(surface("skill", name, str(SOURCE), "claude-user"))

    commands = section(text, "## 5. SLASH COMMANDS", "## 6. CLAUDE WEB")
    for name in re.findall(r"`(/[^`]+)`", commands):
        surfaces.append(surface("slash-command", name, str(SOURCE), "claude-user"))

    third_party = re.search(r"### Third-party MCPs active via plugins\s*\n([^\n]+)", text)
    if third_party:
        for name in named_tokens(third_party.group(1)):
            surfaces.append(surface("mcp", name, str(SOURCE), "claude-plugin"))

    # De-duplicate by stable id while preserving the first source classification.
    unique = {item["id"]: item for item in surfaces}
    inventory = {"version": "1.0.0", "source": str(SOURCE), "counts": counts, "surfaces": sorted(unique.values(), key=lambda x: x["id"])}
    OUT.write_text(json.dumps(inventory, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    entries = catalog.setdefault("entries", [])
    positions = {item.get("id"): i for i, item in enumerate(entries) if isinstance(item, dict)}
    for item in inventory["surfaces"]:
        if item["id"] in positions:
            entries[positions[item["id"]]] = item
        else:
            entries.append(item)
            positions[item["id"]] = len(entries) - 1
    catalog["version"] = "1.4.0"
    CATALOG.write_text(json.dumps(catalog, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"counts": counts, "surfaces": len(inventory["surfaces"]), "status": "review-required"}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
