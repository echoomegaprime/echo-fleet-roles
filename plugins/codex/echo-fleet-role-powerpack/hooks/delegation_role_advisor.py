"""Codex-compatible role classifier. Classification is advisory only."""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path


ROLE_HINTS = {
    "troubleshooter": ("debug", "broken", "failing", "root cause", "traceback", "regression"),
    "pentester": ("pentest", "exploit", "attack path", "red team"),
    "harbormaster": ("deploy", "canary", "rollback", "promotion"),
    "judge": ("certify", "independent verifier", "production_ready"),
    "builder": ("build", "implement", "create", "repair", "fix"),
}


def classify(prompt: str, known_roles: set[str]) -> str | None:
    low = prompt.casefold()
    scored: list[tuple[int, str]] = []
    for role, hints in ROLE_HINTS.items():
        if role not in known_roles:
            continue
        score = sum(len(hint) for hint in hints if re.search(r"(?<![a-z0-9])" + re.escape(hint) + r"(?![a-z0-9])", low))
        if score:
            scored.append((score, role))
    if not scored:
        return None
    scored.sort(reverse=True)
    if len(scored) > 1 and scored[0][0] == scored[1][0]:
        return None
    return scored[0][1]


def main() -> int:
    try:
        payload = json.loads(sys.stdin.read() or "{}")
        prompt = str(payload.get("prompt") or payload.get("user_prompt") or "").strip()
        if not prompt:
            return 0
        plugin_root = Path(os.environ.get("PLUGIN_ROOT", Path(__file__).resolve().parents[1]))
        registry = json.loads((plugin_root / "config" / "role_power_registry.json").read_text(encoding="utf-8"))
        role = classify(prompt, set(registry["roles"]))
        if not role:
            return 0
        context = (
            f"Role classification advisory: this prompt appears aligned with the {role} role. "
            "Compare that recommendation with the live SOL role and use the governed same-session role-switch flow "
            "only when responsibility materially changes. Classification never mutates or proves adoption."
        )
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": context}}))
    except Exception:
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
