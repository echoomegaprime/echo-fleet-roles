"""Fail-open Codex hook that injects the live role and prompt-time switch gate."""

from __future__ import annotations

import json
import os
import re
import sqlite3
import sys
from contextlib import closing
from pathlib import Path
from urllib.parse import quote


def state_path() -> Path:
    configured = os.environ.get("ECHO_ROLE_STATE")
    if configured:
        return Path(configured)
    if os.name == "nt":
        root = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
        return root / "EchoFleetRoles" / "state.sqlite3"
    root = Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local" / "state"))
    return root / "echo-fleet-roles" / "state.sqlite3"


def _read_role(path: Path, query: str, params: tuple[object, ...]) -> str | None:
    if not path.exists():
        return None
    try:
        uri = f"file:{quote(path.resolve().as_posix(), safe='/:')}?mode=ro"
        with closing(sqlite3.connect(uri, uri=True, timeout=2.0)) as connection:
            row = connection.execute(query, params).fetchone()
            return str(row[0]) if row and row[0] else None
    except (OSError, sqlite3.Error):
        return None


def _live_sol_role() -> str | None:
    configured = os.environ.get("SOL_STATE_DB")
    run_id = os.environ.get("SOL_RUN_ID")
    if not configured or not run_id:
        return None
    return _read_role(
        Path(configured),
        "SELECT role FROM missions WHERE run_id=?",
        (run_id,),
    )


def _selected_role(registry: dict[str, object]) -> str:
    roles = registry["roles"]
    assert isinstance(roles, dict)
    candidates = (
        _live_sol_role(),
        _read_role(state_path(), "SELECT role FROM current_role WHERE singleton=1", ()),
        str(registry["default_role"]),
    )
    for candidate in candidates:
        if candidate in roles:
            return candidate
    return str(registry["default_role"])


def _explicit_role(prompt: str, registry: dict[str, object]) -> str | None:
    if not prompt.strip():
        return None
    aliases = registry.get("aliases", {})
    roles = registry["roles"]
    assert isinstance(aliases, dict)
    assert isinstance(roles, dict)
    role_terms: dict[str, str] = {str(name): str(name) for name in roles}
    role_terms.update(
        (str(alias), str(role))
        for alias, role in aliases.items()
        if len(str(alias)) > 1
    )
    intent = r"(?:start|switch|set|use|operate|work|act|continue|serve)"
    for term in sorted(role_terms, key=len, reverse=True):
        variants = {term, term.replace("-", " "), term.replace("_", " ")}
        token = "(?:" + "|".join(re.escape(value) for value in sorted(variants, key=len, reverse=True)) + ")"
        patterns = (
            rf"\b{intent}\b.{{0,120}}?\b(?:as|to|into|under)\s+(?:the\s+)?['\"]?{token}['\"]?(?:\s+(?:fleet\s+)?role)?\b",
            rf"\b{intent}\b.{{0,120}}?\b(?:fleet\s+)?role\b(?:\s+(?:to|as)|\s*[:=])\s*['\"]?{token}['\"]?\b",
        )
        if any(re.search(pattern, prompt, flags=re.IGNORECASE | re.DOTALL) for pattern in patterns):
            return role_terms[term]
    return None


def _prompt_gate(prompt: str, current_role: str, registry: dict[str, object]) -> str:
    explicit = _explicit_role(prompt, registry)
    if explicit:
        if explicit == current_role:
            transition = "The live role already matches; continue without switching."
        else:
            transition = (
                f"The live role is {current_role}; switch before acting through the same-session role switch flow, "
                "then load the returned context packet and primary skill."
            )
        return (
            f" Explicit role directive: {explicit} is pinned for this prompt. {transition} "
            "Do not auto-route to a different role unless the user redirects the objective."
        )
    return (
        " Role selection gate: before acting, compare the prompt's primary responsibility with the live role. "
        "If responsibility materially changes domains, you must perform the governed same-session role switch, "
        "load its returned context packet and primary skill, and then continue. If the live role already owns the "
        "responsibility, continue without switching. Never mutate role state or broker scope outside that flow."
    )


def main() -> int:
    try:
        raw_input = sys.stdin.read()
        hook_input = json.loads(raw_input) if raw_input.strip() else {}
        event_name = hook_input.get("hook_event_name", "SessionStart")
        if event_name not in {"SessionStart", "UserPromptSubmit"}:
            event_name = "SessionStart"
        plugin_root = Path(os.environ.get("PLUGIN_ROOT", Path(__file__).resolve().parents[1]))
        registry = json.loads((plugin_root / "config" / "role_power_registry.json").read_text(encoding="utf-8"))
        role_name = _selected_role(registry)
        role = registry["roles"][role_name]
        context = (
            f"ECHO live fleet role: {role_name}. Load and follow ${role['primary_skill']}. "
            f"Available composed skills: {', '.join(role['composed_skills'])}. "
            f"Authorized capability families declared by the role: {', '.join(role['capability_families'])}. "
            "Use only tools and authority actually exposed by the current host."
        )
        if event_name == "UserPromptSubmit":
            prompt = str(hook_input.get("prompt") or hook_input.get("user_prompt") or "")
            context += _prompt_gate(prompt, role_name, registry)
        print(json.dumps({"hookSpecificOutput": {"hookEventName": event_name, "additionalContext": context}}))
    except Exception:
        # Hooks must never prevent Codex from starting or accepting a prompt.
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
