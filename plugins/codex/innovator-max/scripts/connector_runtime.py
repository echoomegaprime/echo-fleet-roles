"""Typed role/capability resolver with an optional scoped SOL broker invocation.

The registry is deliberately file-based and dependency-free so it can be reviewed,
tested, and used in a fresh clone. It never prints environment variables or secrets.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# Imported unconditionally on purpose. If the policy layer cannot be loaded the
# module must fail loudly -- a try/except here would silently drop the safety
# boundary and leave every caller executing unchecked.
from security import audit, policy

PLUGIN_ROOT = Path(__file__).resolve().parents[1]


def _resolve_repo_root() -> Path:
    """Find the ECHO checkout even when this plugin runs from an installed cache."""
    marker = Path("SYSTEMS") / "codex_auto" / "sol_cli.py"
    here = Path(__file__).resolve()
    cwd = Path.cwd().resolve()
    candidates = (cwd, *cwd.parents, *here.parents, Path("C:/ECHO_OMEGA_PRIME"))
    return next((path for path in candidates if (path / marker).is_file()), here.parents[3])


REPO_ROOT = _resolve_repo_root()
REGISTRY = PLUGIN_ROOT / "registry"
DEFAULT_BROKER = REPO_ROOT / "SYSTEMS" / "codex_auto" / "sol_cli.py"
SECRET_RE = re.compile(r"(?i)(api[_-]?key|token|password|secret|private[_-]?key)\s*[:=]\s*[^,\s}]+")


@dataclass(frozen=True)
class Connector:
    id: str
    capability: str
    description: str
    verbs: tuple[str, ...]
    roles: tuple[str, ...]
    sensitivity: str
    health: str
    broker: str
    keywords: tuple[str, ...]

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "Connector":
        return cls(
            id=raw["id"], capability=raw["capability"], description=raw["description"],
            verbs=tuple(raw.get("verbs", [])), roles=tuple(raw.get("roles", [])),
            sensitivity=raw.get("sensitivity", "internal"), health=raw.get("health", "unknown"),
            broker=raw.get("broker", "sol-sdk"), keywords=tuple(raw.get("keywords", [])),
        )


def load() -> list[Connector]:
    records: list[Connector] = []
    for path in sorted(REGISTRY.glob("connectors/*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        records.extend(Connector.from_dict(item) for item in payload.get("connectors", []))
    return records


def score(connector: Connector, role: str, intent: str, sensitivity: str) -> int:
    if connector.health in {"red", "disabled"} or sensitivity == "restricted" and connector.sensitivity != "restricted":
        return -1
    words = set(re.findall(r"[a-z0-9]+", intent.lower()))
    score_value = 20 if role in connector.roles or "*" in connector.roles else 0
    score_value += 5 * len(words.intersection(set(connector.keywords)))
    score_value += 3 * len(words.intersection(set(re.findall(r"[a-z0-9]+", connector.description.lower()))))
    score_value += 2 if connector.health == "green" else 0
    return score_value


def retrieve(role: str, intent: str, sensitivity: str) -> list[dict[str, Any]]:
    ranked = sorted(((score(item, role, intent, sensitivity), item) for item in load()), key=lambda pair: pair[0], reverse=True)
    return [{"score": points, **item.__dict__} for points, item in ranked if points >= 0]


def redact(value: Any) -> Any:
    if isinstance(value, str):
        return SECRET_RE.sub(lambda match: match.group(1) + "=<redacted>", value)
    if isinstance(value, dict):
        return {key: redact(val) for key, val in value.items()}
    if isinstance(value, list):
        return [redact(item) for item in value]
    return value


def invoke(capability: str, command: str, options: dict[str, Any], broker: Path) -> int:
    """Raw executor. Callers MUST route through guarded_invoke, never here directly."""
    args = [sys.executable, str(broker), "sdk", "invoke", capability, command, "--options", json.dumps(options, separators=(",", ":"))]
    completed = subprocess.run(args, cwd=REPO_ROOT, capture_output=True, text=True, timeout=120)
    output = completed.stdout or completed.stderr
    print(json.dumps({"returncode": completed.returncode, "result": redact(output)}, indent=2))
    return completed.returncode


def guarded_invoke(request: dict[str, Any]) -> dict[str, Any]:
    """The one safety boundary every client shares.

    SKILL.md: "All clients use health, list, retrieve, and invoke. Invocation
    defaults to a plan; execute:true is required for a real call. This is the
    safety and interoperability boundary."

    That was only true of the stdio gateway. The CLI called `invoke` directly and
    so performed real SDK calls with no policy check, no registration check, no
    plan default, and no audit record. Both clients now come through here, which
    is also why the checks are not reimplemented per client -- two copies of a
    boundary drift, and the weaker copy is the one that gets used.

    `op` is forced to "invoke" because `policy()` keys on it and returns
    {"allowed": True, "mode": "read"} for anything else. A request that merely
    forgot to set `op` would otherwise sail through every check.
    """
    request = {**request, "op": "invoke"}
    known = {item.capability for item in load()}

    def refuse(error: str, **extra: Any) -> dict[str, Any]:
        result = {"id": request.get("id"), "ok": False, "error": error, **extra}
        return {**result, "audit": audit(request, result)}

    decision = policy(request, known)
    if not decision["allowed"]:
        return refuse("policy_denied", reason=decision["reason"])

    capability, command = request.get("capability"), request.get("command")
    if not capability or not command:
        return refuse("capability_and_command_required")
    if capability not in known:
        return refuse("capability_not_registered")

    if not request.get("execute", False):
        result = {"id": request.get("id"), "ok": True, "planned": True,
                  "capability": capability, "command": command,
                  "options": redact(request.get("options", {}) or {})}
        return {**result, "audit": audit(request, result)}

    broker = Path(request.get("broker") or DEFAULT_BROKER)
    code = invoke(capability, command, request.get("options", {}) or {}, broker)
    result = {"id": request.get("id"), "ok": code == 0, "planned": False, "capability": capability}
    return {**result, "audit": audit(request, result)}


def health() -> dict[str, Any]:
    """Diagnostic only -- makes no security decision, so it reports faults rather than raising."""
    report: dict[str, Any] = {"ok": True, "registry": str(REGISTRY), "faults": []}
    try:
        connectors = load()
    except (OSError, ValueError, KeyError) as exc:
        report["ok"] = False
        report["faults"].append(f"connector registry unreadable: {exc}")
        connectors = []
    report["connector_count"] = len(connectors)
    tally: dict[str, int] = {}
    for item in connectors:
        tally[item.health] = tally.get(item.health, 0) + 1
    report["connector_health"] = tally

    roles_path = REGISTRY / "roles.json"
    try:
        report["role_count"] = len(json.loads(roles_path.read_text(encoding="utf-8")).get("roles", []))
    except (OSError, ValueError) as exc:
        report["ok"] = False
        report["role_count"] = 0
        report["faults"].append(f"{roles_path.name} unreadable: {exc}")
    report["broker_present"] = DEFAULT_BROKER.is_file()
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Resolve role-aware ECHO connectors")
    sub = parser.add_subparsers(dest="action", required=True)
    sub.add_parser("health")
    sub.add_parser("list")
    find = sub.add_parser("retrieve")
    find.add_argument("--role", required=True)
    find.add_argument("--intent", required=True)
    find.add_argument("--sensitivity", default="internal")
    call = sub.add_parser("invoke")
    call.add_argument("capability")
    call.add_argument("command")
    call.add_argument("--options", default="{}")
    call.add_argument("--role", help="required by policy for a real call")
    call.add_argument("--sensitivity", default="internal")
    # Opt-in, never a default: without it the CLI returns a plan and touches nothing.
    call.add_argument("--execute", action="store_true",
                      help="perform the real call (default is a plan only)")
    call.add_argument("--broker", default=str(DEFAULT_BROKER))
    args = parser.parse_args()
    if args.action == "health":
        report = health()
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0 if report["ok"] else 1
    if args.action == "list":
        print(json.dumps([item.__dict__ for item in load()], indent=2, sort_keys=True))
        return 0
    if args.action == "retrieve":
        print(json.dumps(retrieve(args.role, args.intent, args.sensitivity), indent=2, sort_keys=True))
        return 0

    try:
        options = json.loads(args.options)
    except json.JSONDecodeError as exc:
        print(json.dumps({"ok": False, "error": "invalid_options_json", "detail": str(exc)}), file=sys.stderr)
        return 2
    response = guarded_invoke({
        "capability": args.capability, "command": args.command, "options": options,
        "role": args.role, "sensitivity": args.sensitivity,
        "execute": args.execute, "broker": args.broker,
    })
    print(json.dumps(redact(response), indent=2, sort_keys=True))
    return 0 if response.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
