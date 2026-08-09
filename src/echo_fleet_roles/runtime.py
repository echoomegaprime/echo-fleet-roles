from __future__ import annotations

from pathlib import Path
from typing import Any

from .registry import Registry, load_registry
from .state import RoleState


class RoleRuntime:
    def __init__(
        self,
        registry: Registry | None = None,
        *,
        registry_path: str | Path | None = None,
        state_path: str | Path | None = None,
    ) -> None:
        self.registry = registry or load_registry(registry_path)
        self.state = RoleState(state_path)

    def current(self) -> dict[str, Any]:
        name = self.state.current(self.registry.default_role)
        return self.context(name)

    def switch(
        self,
        role: str,
        *,
        expected_current: str | None = None,
        idempotency_key: str | None = None,
        reason: str | None = None,
    ) -> dict[str, Any]:
        resolved = self.registry.resolve(role)
        expected = self.registry.resolve(expected_current) if expected_current else None
        transition = self.state.switch(
            resolved,
            self.registry.default_role,
            expected_current=expected,
            idempotency_key=idempotency_key,
            metadata={"reason": reason} if reason else {},
        )
        return {"transition": transition.as_dict(), "context": self.context(resolved)}

    def context(self, role: str) -> dict[str, Any]:
        selected = self.registry.role(role)
        return {
            "role": selected.name,
            "primary_skill": selected.primary_skill,
            "composed_skills": list(selected.composed_skills),
            "scopes": list(selected.scopes),
            "capability_families": list(selected.capability_families),
            "requires_new_process": False,
            "requires_new_session": False,
            "activation_instruction": (
                f"Operate as the {selected.name} role. Read and follow ${selected.primary_skill}; "
                "load composed skills only when their domains apply; use only currently exposed and authorized tools."
            ),
        }
