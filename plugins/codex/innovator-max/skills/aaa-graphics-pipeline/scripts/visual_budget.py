"""Visual budget checker for the AAA graphics pipeline skill.

Reads a budget declaration and a measured report, then answers one question: does
this asset fit? Exits non-zero when it does not, so a build gate can call it
directly.

The skill's SKILL.md referenced this file for weeks while it existed nowhere. The
bundle served the instructions with `ok: true` and omitted the code, which is the
exact failure the pipeline's own evidence contract forbids.

    python scripts/visual_budget.py --budget budget.json --report measured.json

Both files are flat {metric: number}. Metrics absent from the budget are reported
as unbudgeted rather than silently passed -- an unmeasured metric is not a pass.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


# Lower is better for everything here; a "max" budget is the only shape that makes
# sense for polys, textures, draw calls, and frame time.
DEFAULT_BUDGET: dict[str, float] = {
    "triangles": 150_000,
    "draw_calls": 200,
    "texture_mb": 512,
    "material_count": 24,
    "frame_ms": 16.6,
}


def load(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SystemExit(f"visual_budget: file not found: {path}")
    except json.JSONDecodeError as exc:
        raise SystemExit(f"visual_budget: {path} is not valid JSON: {exc}")


def evaluate(budget: dict[str, float], report: dict[str, float]) -> dict[str, Any]:
    violations: list[dict[str, Any]] = []
    checked: list[dict[str, Any]] = []
    for metric, limit in budget.items():
        if metric not in report:
            violations.append({"metric": metric, "reason": "not_measured", "limit": limit})
            continue
        measured = float(report[metric])
        row = {
            "metric": metric,
            "measured": measured,
            "limit": float(limit),
            "headroom_pct": round((1 - measured / float(limit)) * 100, 1) if limit else 0.0,
        }
        checked.append(row)
        if measured > float(limit):
            violations.append({**row, "reason": "over_budget"})

    unbudgeted = sorted(set(report) - set(budget))
    return {
        "ok": not violations,
        "checked": checked,
        "violations": violations,
        "unbudgeted_metrics": unbudgeted,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="AAA visual budget gate")
    parser.add_argument("--budget", type=Path, help="budget JSON; defaults apply when omitted")
    parser.add_argument("--report", type=Path, required=True, help="measured metrics JSON")
    parser.add_argument("--json", action="store_true", help="machine-readable output only")
    args = parser.parse_args(argv)

    budget = load(args.budget) if args.budget else dict(DEFAULT_BUDGET)
    result = evaluate(budget, load(args.report))

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        for row in result["checked"]:
            print(f"  {row['metric']:<16} {row['measured']:>12,.1f} / {row['limit']:>12,.1f}"
                  f"  ({row['headroom_pct']:+.1f}% headroom)")
        for violation in result["violations"]:
            print(f"  VIOLATION {violation['metric']}: {violation['reason']}", file=sys.stderr)
        if result["unbudgeted_metrics"]:
            print(f"  unbudgeted: {', '.join(result['unbudgeted_metrics'])}")
        print("PASS" if result["ok"] else "FAIL")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
