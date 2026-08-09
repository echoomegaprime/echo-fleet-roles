from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


class RegistryError(ValueError):
    """Raised when the role registry violates its contract."""


@dataclass(frozen=True)
class Role:
    name: str
    primary_skill: str
    composed_skills: tuple[str, ...]
    scopes: tuple[str, ...]
    capability_families: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "primary_skill": self.primary_skill,
            "composed_skills": list(self.composed_skills),
            "scopes": list(self.scopes),
            "capability_families": list(self.capability_families),
        }


@dataclass(frozen=True)
class Registry:
    schema_version: int
    default_role: str
    default_plugin: str
    aliases: Mapping[str, str]
    roles: Mapping[str, Role]

    def resolve(self, value: str) -> str:
        candidate = value.strip().lower().replace(" ", "-")
        candidate = self.aliases.get(candidate, candidate)
        if candidate not in self.roles:
            available = ", ".join(sorted(self.roles))
            raise RegistryError(f"Unknown role '{value}'. Available roles: {available}")
        return candidate

    def role(self, value: str) -> Role:
        return self.roles[self.resolve(value)]


def _string_list(value: Any, field: str, role_name: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not value or not all(isinstance(item, str) and item.strip() for item in value):
        raise RegistryError(f"roles.{role_name}.{field} must be a non-empty string array")
    if len(value) != len(set(value)):
        raise RegistryError(f"roles.{role_name}.{field} contains duplicate values")
    return tuple(value)


def parse_registry(payload: Mapping[str, Any]) -> Registry:
    if payload.get("schema_version") != 2:
        raise RegistryError("schema_version must be 2")
    default_role = payload.get("default_role")
    default_plugin = payload.get("default_plugin")
    aliases = payload.get("aliases")
    roles_payload = payload.get("roles")
    if not isinstance(default_role, str) or not default_role:
        raise RegistryError("default_role must be a non-empty string")
    if not isinstance(default_plugin, str) or not default_plugin:
        raise RegistryError("default_plugin must be a non-empty string")
    if not isinstance(aliases, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in aliases.items()):
        raise RegistryError("aliases must be a string-to-string object")
    if not isinstance(roles_payload, dict) or not roles_payload:
        raise RegistryError("roles must be a non-empty object")

    roles: dict[str, Role] = {}
    for role_name, raw in roles_payload.items():
        if not isinstance(role_name, str) or not isinstance(raw, dict):
            raise RegistryError("each role must be a named object")
        allowed = {"primary_skill", "composed_skills", "scopes", "capability_families"}
        extra = set(raw) - allowed
        if extra:
            raise RegistryError(f"roles.{role_name} contains unsupported fields: {sorted(extra)}")
        primary = raw.get("primary_skill")
        if not isinstance(primary, str) or not primary.strip():
            raise RegistryError(f"roles.{role_name}.primary_skill must be a non-empty string")
        roles[role_name] = Role(
            name=role_name,
            primary_skill=primary,
            composed_skills=_string_list(raw.get("composed_skills"), "composed_skills", role_name),
            scopes=_string_list(raw.get("scopes"), "scopes", role_name),
            capability_families=_string_list(raw.get("capability_families"), "capability_families", role_name),
        )

    if len(roles) != 30:
        raise RegistryError(f"registry must contain exactly 30 roles, found {len(roles)}")
    if default_role not in roles:
        raise RegistryError("default_role does not name a registered role")
    for alias, role_name in aliases.items():
        if not alias or role_name not in roles:
            raise RegistryError(f"alias '{alias}' targets unknown role '{role_name}'")
    return Registry(2, default_role, default_plugin, dict(aliases), roles)


def default_registry_path() -> Path:
    return Path(__file__).resolve().parent / "data" / "role_power_registry.json"


def load_registry(path: str | Path | None = None) -> Registry:
    source = Path(path) if path else default_registry_path()
    try:
        payload = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RegistryError(f"Unable to load registry {source}: {exc}") from exc
    if not isinstance(payload, dict):
        raise RegistryError("registry root must be an object")
    return parse_registry(payload)
