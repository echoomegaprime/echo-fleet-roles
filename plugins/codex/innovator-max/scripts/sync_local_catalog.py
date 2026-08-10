#!/usr/bin/env python3
"""Import installed Codex/Agent skills and plugin manifests into the ECHO catalog.

This is an inventory operation, not an approval bypass. Imported entries remain
review-required until provenance, permissions, tests, and supply-chain checks
are completed by a role reviewer.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tomllib
from pathlib import Path
from typing import Any


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
REGISTRY = PLUGIN_ROOT / "registry"
CATALOG_PATH = REGISTRY / "catalog.json"
INVENTORY_PATH = REGISTRY / "local_inventory.json"


def _home(name: str, fallback: str) -> Path:
    return Path(os.environ.get(name, fallback)).expanduser()


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def _skill_metadata(path: Path) -> dict[str, str]:
    text = (path / "SKILL.md").read_text(encoding="utf-8", errors="replace")
    title = path.name
    match = re.search(r"^name:\s*[\"']?(.+?)[\"']?\s*$", text, re.MULTILINE)
    if match:
        title = match.group(1).strip()
    description = ""
    frontmatter = re.search(r"description:\s*[\"']?(.+?)[\"']?\s*$", text, re.MULTILINE)
    if frontmatter:
        description = frontmatter.group(1).strip()
    return {"name": title, "description": description}


def _path_key(path: Path) -> str:
    return hashlib.sha256(str(path.resolve()).lower().encode("utf-8")).hexdigest()[:12]


def _marketplace_entries(path: Path) -> list[dict[str, Any]]:
    payload = _read_json(path)
    marketplace = str(payload.get("name") or path.parent.name)
    records: list[dict[str, Any]] = []
    for plugin in payload.get("plugins", []):
        if not isinstance(plugin, dict) or not plugin.get("name"):
            continue
        source = plugin.get("source", {}) if isinstance(plugin.get("source"), dict) else {}
        records.append({
            "id": f"available:codex-plugin:{marketplace}:{plugin['name']}",
            "name": str(plugin["name"]),
            "kind": "plugin",
            "provider": marketplace,
            "source": str(path),
            "source_type": str(source.get("source") or "unknown"),
            "source_locator": str(source.get("path") or source.get("url") or source.get("repo") or ""),
            "category": str(plugin.get("category") or "Uncategorized"),
            "status": "available-review-required",
            "roles": ["all"],
            "permissions": ["plugin.retrieve"],
            "installation_policy": plugin.get("policy", {}),
        })
    return records


def discover() -> dict[str, Any]:
    codex_root = _home("CODEX_HOME", str(Path.home() / ".codex"))
    plugin_cache = codex_root / "plugins" / "cache"
    skill_roots = [codex_root / "skills", Path.home() / ".agents" / "skills", plugin_cache]
    skills: list[dict[str, Any]] = []
    seen_skill_paths: set[Path] = set()
    for root in skill_roots:
        if not root.is_dir():
            continue
        for skill_file in sorted(root.rglob("SKILL.md")):
            resolved = skill_file.resolve()
            if resolved in seen_skill_paths:
                continue
            seen_skill_paths.add(resolved)
            meta = _skill_metadata(skill_file.parent)
            skills.append({
                "id": f"installed:skill:{re.sub(r'[^a-z0-9-]+', '-', meta['name'].lower()).strip('-')}:{_path_key(skill_file)}",
                "name": meta["name"],
                "description": meta["description"],
                "kind": "skill",
                "provider": "codex-plugin-cache" if plugin_cache in skill_file.parents else "codex-local",
                "source": str(skill_file.parent),
                "status": "installed-review-required",
                "roles": ["all"],
                "permissions": ["skill.retrieve"],
            })

    plugin_roots = [plugin_cache]
    plugins: list[dict[str, Any]] = []
    surfaces: list[dict[str, Any]] = []
    for root in plugin_roots:
        if not root.is_dir():
            continue
        for manifest_path in sorted(root.rglob(".codex-plugin/plugin.json")):
            manifest = _read_json(manifest_path)
            name = str(manifest.get("name") or manifest_path.parent.parent.name)
            # This plugin already has a canonical published entry. Importing its
            # cache-busted installed copy would create a stale self-reference on
            # every reinstall and duplicate its MCP surface.
            if name == "innovator-max":
                continue
            version = str(manifest.get("version") or "unknown")
            entry_id = f"installed:plugin:{name}:{version}"
            plugins.append({
                "id": entry_id,
                "name": name,
                "version": version,
                "description": str(manifest.get("description") or ""),
                "kind": "plugin",
                "provider": "openai-curated-or-local",
                "source": str(manifest_path.parent.parent),
                "repository": manifest.get("repository", ""),
                "license": manifest.get("license", "unknown"),
                "status": "installed-review-required",
                "roles": ["all"],
                "permissions": ["plugin.retrieve"],
                "surfaces": [k for k in ("skills", "mcpServers", "apps") if k in manifest],
            })
            for field, kind, permission in (
                ("mcpServers", "connector", "connector.retrieve"),
                ("apps", "app-connector", "connector.retrieve"),
            ):
                if field in manifest:
                    surfaces.append({
                        "id": f"installed:{field}:{name}:{version}",
                        "name": f"{name} {field}",
                        "kind": kind,
                        "provider": "openai-curated-or-local",
                        "source": str(manifest_path.parent.parent),
                        "status": "installed-review-required",
                        "roles": ["all"],
                        "permissions": [permission],
                        "parent_plugin": entry_id,
                    })

    config_path = codex_root / "config.toml"
    if config_path.is_file():
        try:
            config = tomllib.loads(config_path.read_text(encoding="utf-8"))
        except (OSError, tomllib.TOMLDecodeError):
            config = {}
        for name, definition in sorted(config.get("mcp_servers", {}).items()):
            if not isinstance(definition, dict):
                continue
            transport = "http" if definition.get("url") else "stdio"
            surfaces.append({
                "id": f"installed:mcp:{name}",
                "name": str(name),
                "kind": "mcp",
                "provider": "codex-config",
                "source": str(config_path),
                "transport": transport,
                "endpoint": str(definition.get("url") or definition.get("command") or ""),
                "status": "installed-review-required",
                "roles": ["all"],
                "permissions": ["connector.retrieve"],
            })

    marketplace_paths = [Path.home() / ".agents" / "plugins" / "marketplace.json"]
    marketplace_paths.extend(sorted((codex_root / ".tmp" / "plugins").glob("**/marketplace.json")))
    available: list[dict[str, Any]] = []
    seen_marketplaces: set[Path] = set()
    for marketplace_path in marketplace_paths:
        resolved = marketplace_path.resolve()
        if resolved in seen_marketplaces or not marketplace_path.is_file():
            continue
        seen_marketplaces.add(resolved)
        available.extend(_marketplace_entries(marketplace_path))
    return {"version": "1.1.0", "skills": skills, "plugins": plugins, "connectors": surfaces, "available_plugins": available}


def merge_catalog(inventory: dict[str, Any]) -> dict[str, Any]:
    catalog = _read_json(CATALOG_PATH)
    entries = [
        entry for entry in catalog.setdefault("entries", [])
        if isinstance(entry, dict)
        and not str(entry.get("id", "")).startswith(("installed:", "available:codex-plugin:"))
    ]
    catalog["entries"] = entries
    positions = {entry.get("id"): index for index, entry in enumerate(entries) if isinstance(entry, dict)}
    for group in ("skills", "plugins", "connectors", "available_plugins"):
        for entry in inventory[group]:
            if entry["id"] in positions:
                entries[positions[entry["id"]]] = entry
            else:
                entries.append(entry)
                positions[entry["id"]] = len(entries) - 1
    catalog["version"] = "1.4.0"
    return catalog


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-merge", action="store_true", help="write inventory only")
    args = parser.parse_args()
    inventory = discover()
    REGISTRY.mkdir(parents=True, exist_ok=True)
    INVENTORY_PATH.write_text(json.dumps(inventory, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if not args.no_merge:
        CATALOG_PATH.write_text(json.dumps(merge_catalog(inventory), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "skills": len(inventory["skills"]),
        "plugins": len(inventory["plugins"]),
        "connectors": len(inventory["connectors"]),
        "available_plugins": len(inventory["available_plugins"]),
        "catalog": str(CATALOG_PATH),
        "inventory": str(INVENTORY_PATH),
        "status": "review-required",
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
