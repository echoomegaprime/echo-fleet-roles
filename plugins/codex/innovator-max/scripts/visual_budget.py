"""Validate explicit visual performance budgets without inspecting secrets."""
from __future__ import annotations

import argparse
import json


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gpu-ms", type=float, required=True)
    parser.add_argument("--gpu-budget-ms", type=float, required=True)
    parser.add_argument("--memory-mb", type=float, required=True)
    parser.add_argument("--memory-budget-mb", type=float, required=True)
    parser.add_argument("--shader-variants", type=int, required=True)
    parser.add_argument("--shader-variant-budget", type=int, required=True)
    args = parser.parse_args()
    checks = {
        "gpu": args.gpu_ms <= args.gpu_budget_ms,
        "memory": args.memory_mb <= args.memory_budget_mb,
        "shader_variants": args.shader_variants <= args.shader_variant_budget,
    }
    result = {"pass": all(checks.values()), "checks": checks, "inputs": vars(args)}
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
