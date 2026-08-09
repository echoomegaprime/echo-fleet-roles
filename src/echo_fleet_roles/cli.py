from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from .registry import RegistryError, load_registry
from .runtime import RoleRuntime
from .state import StateConflict


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="echo-role", description="Select and inspect ECHO fleet roles")
    parser.add_argument("--registry", help="Path to a role registry JSON file")
    parser.add_argument("--state", help="Path to the role state SQLite database")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list", help="List available roles")
    sub.add_parser("current", help="Show the selected role")
    context = sub.add_parser("context", help="Show a role context packet")
    context.add_argument("role", nargs="?", help="Role name or alias; current role when omitted")
    switch = sub.add_parser("switch", help="Switch role without restarting the terminal")
    switch.add_argument("role")
    switch.add_argument("--expected-current")
    switch.add_argument("--idempotency-key")
    switch.add_argument("--reason")
    history = sub.add_parser("history", help="Show recent transitions")
    history.add_argument("--limit", type=int, default=20)
    sub.add_parser("validate", help="Validate the registry")
    return parser


def _emit(payload: Any, as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    elif isinstance(payload, list):
        for item in payload:
            print(item if isinstance(item, str) else json.dumps(item, sort_keys=True))
    elif isinstance(payload, dict):
        for key, value in payload.items():
            print(f"{key}: {json.dumps(value) if isinstance(value, (dict, list)) else value}")
    else:
        print(payload)


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        registry = load_registry(args.registry)
        runtime = RoleRuntime(registry, state_path=args.state)
        if args.command == "list":
            payload = [registry.roles[name].as_dict() for name in sorted(registry.roles)]
        elif args.command == "current":
            payload = runtime.current()
        elif args.command == "context":
            payload = runtime.context(args.role) if args.role else runtime.current()
        elif args.command == "switch":
            payload = runtime.switch(
                args.role,
                expected_current=args.expected_current,
                idempotency_key=args.idempotency_key,
                reason=args.reason,
            )
        elif args.command == "history":
            payload = [item.as_dict() for item in runtime.state.history(args.limit)]
        else:
            payload = {"valid": True, "roles": len(registry.roles), "default_role": registry.default_role}
        _emit(payload, args.json)
        return 0
    except (RegistryError, StateConflict, OSError) as exc:
        print(f"echo-role: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
