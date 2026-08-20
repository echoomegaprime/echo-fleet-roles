"""Pure, host-neutral role resolution and adoption-receipt validation."""

from __future__ import annotations

import hashlib
import json
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Collection, Mapping


RECEIPT_KIND = "echo.role-adoption"
RECEIPT_SCHEMA_VERSION = 1
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
PLUGIN_REVISION_RE = re.compile(r"^sha256:[0-9a-f]{64}$")


@dataclass(frozen=True)
class RoleResolution:
    role: str
    source: str


def compute_plugin_revision(plugin_root: str | Path) -> str:
    """Return a deterministic content revision for the installed routing package."""
    root = Path(plugin_root).resolve()
    paths = [
        root / ".codex-plugin" / "plugin.json",
        root / "config" / "role_power_registry.json",
        *sorted((root / "hooks").glob("*.py")),
    ]
    digest = hashlib.sha256()
    for source in paths:
        relative = source.relative_to(root).as_posix().encode("utf-8")
        digest.update(len(relative).to_bytes(4, "big"))
        digest.update(relative)
        content = source.read_bytes()
        digest.update(len(content).to_bytes(8, "big"))
        digest.update(content)
    return f"sha256:{digest.hexdigest()}"


def make_adoption_receipt(
    *,
    role: str,
    child_session_id: str,
    child_revision: str,
    plugin_revision: str,
    issued_at: int | None = None,
) -> dict[str, Any]:
    """Create data that can be transported by any host without a native Skill tool."""
    normalized_revision = child_revision.casefold()
    normalized_plugin_revision = plugin_revision.casefold()
    if not role.strip() or not child_session_id.strip():
        raise ValueError("role and child_session_id are required")
    if not COMMIT_RE.fullmatch(normalized_revision):
        raise ValueError("child_revision must be an exact 40-character Git SHA")
    if not PLUGIN_REVISION_RE.fullmatch(normalized_plugin_revision):
        raise ValueError("plugin_revision must be a sha256 content revision")
    return {
        "schema_version": RECEIPT_SCHEMA_VERSION,
        "kind": RECEIPT_KIND,
        "role": role.strip(),
        "child_session_id": child_session_id.strip(),
        "child_revision": normalized_revision,
        "plugin_revision": normalized_plugin_revision,
        "issued_at": int(time.time() if issued_at is None else issued_at),
    }


def parse_receipt(value: object) -> Mapping[str, Any] | None:
    if isinstance(value, Mapping):
        return value
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        return None
    return parsed if isinstance(parsed, Mapping) else None


def receipt_matches(
    receipt: object,
    *,
    roles: Collection[str],
    child_session_id: str | None,
    child_revision: str | None,
    plugin_revision: str,
) -> bool:
    parsed = parse_receipt(receipt)
    if parsed is None or not child_session_id or not child_revision:
        return False
    role = parsed.get("role")
    return bool(
        parsed.get("schema_version") == RECEIPT_SCHEMA_VERSION
        and parsed.get("kind") == RECEIPT_KIND
        and isinstance(role, str)
        and role in roles
        and parsed.get("child_session_id") == child_session_id
        and parsed.get("child_revision") == child_revision.casefold()
        and parsed.get("plugin_revision") == plugin_revision.casefold()
        and isinstance(parsed.get("issued_at"), int)
    )


def resolve_role(
    *,
    roles: Collection[str],
    default_role: str,
    live_sol_role: str | None,
    child_receipt: object,
    plugin_role: str | None,
    child_session_id: str | None,
    child_revision: str | None,
    plugin_revision: str,
) -> RoleResolution:
    """Resolve exactly: live SOL, bound child receipt, plugin state, default."""
    known = frozenset(roles)
    if default_role not in known:
        raise ValueError("default_role must name a registered role")
    if live_sol_role in known:
        return RoleResolution(str(live_sol_role), "live_sol")
    if receipt_matches(
        child_receipt,
        roles=known,
        child_session_id=child_session_id,
        child_revision=child_revision,
        plugin_revision=plugin_revision,
    ):
        parsed = parse_receipt(child_receipt)
        assert parsed is not None
        return RoleResolution(str(parsed["role"]), "bound_child_receipt")
    if plugin_role in known:
        return RoleResolution(str(plugin_role), "plugin")
    return RoleResolution(default_role, "default")
