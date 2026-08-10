"""Produce real capture evidence by driving the ECHO render worker.

`aaa_asset_gate.py` demands a `visual_qa.captures` block with a SHA-256 per fixed
camera. Nothing generated those, so in practice they were typed in — and until
today the gate only checked they were 64 hex characters. This closes the loop:
render each camera for real, hash what actually landed on disk, and emit a block
the gate can verify with `--verify-captures`.

    python capture_evidence.py --asset-id hero-01 --cameras front,side,top \\
        --out-dir /tmp/echo-render/hero-01 --emit captures.json

    python aaa_asset_gate.py manifest.json --verify-captures /tmp/echo-render

Talks to `echo-render.service` over HTTP (loopback by default). A camera whose
render fails is reported with `passed: false` and no digest, never silently
dropped — a missing capture must look like a missing capture, not like a
smaller-but-complete set.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

DEFAULT_BASE = "http://127.0.0.1:8412"
# Fixed rigs, so two runs of the same asset are comparable. The gate wants
# *fixed* cameras precisely so a regression shows up as a digest change.
CAMERA_PRESETS: dict[str, dict[str, Any]] = {
    "front": {"width": 960, "height": 720},
    "side": {"width": 960, "height": 720},
    "top": {"width": 960, "height": 720},
    "detail": {"width": 1280, "height": 960, "samples": 256},
}


def render(base: str, token: str, spec: dict[str, Any], timeout: int = 1800) -> dict[str, Any]:
    request = urllib.request.Request(
        base.rstrip("/") + "/render",
        method="POST",
        data=json.dumps(spec).encode(),
    )
    request.add_header("Content-Type", "application/json")
    request.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8", "replace"))
    except urllib.error.HTTPError as exc:
        try:
            return json.loads(exc.read().decode("utf-8", "replace"))
        except (ValueError, OSError):
            return {"ok": False, "error": f"http_{exc.code}"}
    except (urllib.error.URLError, OSError) as exc:
        return {"ok": False, "error": f"unreachable: {exc}"}


def capture(
    base: str, token: str, asset_id: str, cameras: list[str], out_dir: Path,
    samples: int, device: str,
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for camera in cameras:
        preset = dict(CAMERA_PRESETS.get(camera, {"width": 960, "height": 720}))
        preset.setdefault("samples", samples)
        target = out_dir / f"{asset_id}-{camera}.png"
        outcome = render(base, token, {
            "output": str(target), "device": device, **preset,
        })
        row: dict[str, Any] = {"camera": camera, "passed": bool(outcome.get("ok"))}
        if outcome.get("ok"):
            produced = Path(str(outcome.get("output") or target))
            row["path"] = produced.name
            row["sha256"] = str(outcome.get("sha256") or "")
            row["bytes"] = outcome.get("bytes")
            row["node"] = outcome.get("node")
            row["device"] = (outcome.get("device") or {}).get("scene_device")
        else:
            # Reported, not dropped. A failed camera must be visible in the
            # evidence, or the manifest quietly describes a smaller asset.
            row["error"] = outcome.get("error") or "render_failed"
        results.append(row)
    return results


def reconcile(captures: list[dict[str, Any]], root: Path) -> list[str]:
    """Re-hash locally what the worker reported, before anyone trusts it.

    The worker already hashes its output; hashing again here is deliberate. The
    two digests are produced by different processes reading the same file, so a
    mismatch means the artifact changed between render and manifest — exactly the
    window a stale or overwritten capture would slip through.
    """
    problems: list[str] = []
    for row in captures:
        if not row.get("passed"):
            continue
        path = root / str(row.get("path", ""))
        if not path.is_file():
            problems.append(f"{row['camera']}: worker reported success but {path.name} is absent")
            continue
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != row.get("sha256"):
            problems.append(
                f"{row['camera']}: worker digest {str(row.get('sha256'))[:16]}… "
                f"!= local {actual[:16]}…"
            )
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="render real AAA capture evidence")
    parser.add_argument("--asset-id", required=True)
    parser.add_argument("--cameras", default="front,side,top",
                        help="comma-separated; the gate wants >=3 for shader assets")
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--emit", type=Path, help="write the captures block here")
    parser.add_argument("--base", default=DEFAULT_BASE)
    parser.add_argument("--token", default="", help="or set ECHO_RENDER_TOKEN")
    parser.add_argument("--samples", type=int, default=64)
    parser.add_argument("--device", default="auto", choices=("auto", "gpu", "cpu"))
    args = parser.parse_args(argv)

    import os
    token = args.token or os.environ.get("ECHO_RENDER_TOKEN", "")
    if not token:
        print(json.dumps({"ok": False, "error": "no render token (--token or ECHO_RENDER_TOKEN)"}))
        return 2

    cameras = [c.strip() for c in args.cameras.split(",") if c.strip()]
    args.out_dir.mkdir(parents=True, exist_ok=True)
    captures = capture(args.base, token, args.asset_id, cameras,
                       args.out_dir, args.samples, args.device)
    problems = reconcile(captures, args.out_dir)

    block = {
        "asset_id": args.asset_id,
        "visual_qa": {"captures": captures},
        "capture_root": str(args.out_dir),
        "rendered": sum(1 for c in captures if c.get("passed")),
        "requested": len(cameras),
        "reconciliation_problems": problems,
    }
    if args.emit:
        args.emit.write_text(json.dumps(block, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(block, indent=2))
    return 0 if block["rendered"] == block["requested"] and not problems else 1


if __name__ == "__main__":
    raise SystemExit(main())
