"""Fail-closed evidence gate for an AAA visual-production claim.

The structural checks below are thorough, but every SHA-256 in a manifest was
only ever checked against `HASH_RE` -- i.e. "is this 64 hex characters". Sixty-four
arbitrary hex digits passed. The whole evidence contract was self-asserted, which
made this a gate that could not fail on the thing it exists to gate.

`--verify-captures ROOT` closes that: each capture must carry a `path` that
resolves inside ROOT and whose real digest equals the declared one. Without the
flag the behaviour is unchanged, but the result now always reports
`hashes_verified` so a consumer can tell self-asserted evidence from checked
evidence instead of assuming.

Render real captures with `capture_evidence.py`, which drives the ECHO render
worker and emits paths and digests it actually produced.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

HASH_RE = re.compile(r"^[0-9a-f]{64}$")
FORBIDDEN_RE = re.compile(r"\b(todo|placeholder|stub|tbd|fixme)\b", re.IGNORECASE)
SHADER_ASSETS = {"interactive-3d", "game", "web-3d"}
READ_CHUNK = 1 << 20


def _digest(path: Path) -> str:
    sha = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(READ_CHUNK):
            sha.update(chunk)
    return sha.hexdigest()


def _verify_one(item: Any, safe_root: Path, label: str, digest_key: str) -> str | None:
    """Check one declared artifact against the file it names. None = verified.

    Shared by captures and shader compile results deliberately. Two copies of a
    path-confinement check drift, and the copy that drifts is the one that stops
    refusing `../../etc/passwd`.
    """
    if not isinstance(item, dict):
        return f"{label} is not an object"
    declared = str(item.get(digest_key, ""))
    relative = str(item.get("path", "")).strip()
    if not relative:
        return f"{label} has no 'path'; a digest with no file cannot be verified"
    candidate = (safe_root / relative).resolve()
    try:
        candidate.relative_to(safe_root)
    except ValueError:
        return f"{label} path {relative!r} escapes the verification root"
    if not candidate.is_file():
        return f"{label} path {relative!r} does not exist under the verification root"
    actual = _digest(candidate)
    if actual != declared:
        return (f"{label} digest mismatch for {relative!r}: declared {declared[:16]}… "
                f"actual {actual[:16]}…")
    return None


def _safe_root(root: Path) -> tuple[Path | None, str | None]:
    try:
        return root.resolve(strict=True), None
    except OSError as exc:
        return None, f"verification root unreadable: {exc}"


def verify_captures(captures: list[Any], root: Path) -> list[str]:
    """Re-hash every declared capture. Returns a list of failures (empty = all good).

    Confinement matters as much as the digest: a manifest that can name
    `../../etc/passwd` and have the gate hash it is an arbitrary-read primitive.
    """
    safe_root, error = _safe_root(root)
    if safe_root is None:
        return [error or "verification root unreadable"]
    return [
        problem for index, item in enumerate(captures)
        if (problem := _verify_one(item, safe_root, f"capture[{index}]", "sha256"))
    ]


def verify_shader_artifacts(shaders: list[Any], root: Path) -> list[str]:
    """Re-hash every declared shader compile artifact.

    `artifact_sha256` had exactly the weakness captures had: checked against a
    64-hex regex and never against a file, so a manifest could claim every target
    backend compiled cleanly and produce nothing. This cannot compile a shader --
    it refuses to accept a compile claim that names no verifiable artifact, which
    is the honest half of the problem.
    """
    safe_root, error = _safe_root(root)
    if safe_root is None:
        return [error or "verification root unreadable"]
    failures: list[str] = []
    for shader_index, shader in enumerate(shaders):
        if not isinstance(shader, dict):
            failures.append(f"shader[{shader_index}] is not an object")
            continue
        name = str(shader.get("name") or shader_index)
        results = shader.get("compile_results")
        if not isinstance(results, list) or not results:
            failures.append(f"shader[{name}] declares no compile_results to verify")
            continue
        for result_index, result in enumerate(results):
            backend = result.get("backend") if isinstance(result, dict) else result_index
            label = f"shader[{name}].compile_results[{backend}]"
            if problem := _verify_one(result, safe_root, label, "artifact_sha256"):
                failures.append(problem)
    return failures


def _at(value: dict[str, Any], path: str) -> Any:
    current: Any = value
    for key in path.split("."):
        if not isinstance(current, dict) or key not in current:
            return None
        current = current[key]
    return current


def validate(data: dict[str, Any], capture_root: Path | None = None) -> dict[str, Any]:
    failures: list[str] = []
    checks: dict[str, bool] = {}
    hashes_verified = False

    def check(name: str, condition: bool, detail: str) -> None:
        checks[name] = bool(condition)
        if not condition:
            failures.append(detail)

    asset_type = data.get("asset_type")
    check("schema", data.get("schema_version") == 1, "schema_version must equal 1")
    check("identity", bool(data.get("asset_id")) and asset_type in SHADER_ASSETS | {"motion", "static"}, "asset_id and a supported asset_type are required")
    check("art_direction", all(_at(data, f"art_direction.{field}") for field in ("brief", "palette", "focal_hierarchy", "references")), "art_direction needs brief, palette, focal_hierarchy, and references")
    check("color_pipeline", all(_at(data, f"color.{field}") for field in ("working_space", "display_space", "tone_mapper")) and _at(data, "color.hdr_sdr_tested") is True, "color pipeline and HDR/SDR test evidence are required")
    check("accessibility", all(_at(data, f"accessibility.{field}") is True for field in ("reduced_motion", "color_vision", "contrast")), "reduced-motion, color-vision, and contrast checks must pass")

    captures = _at(data, "visual_qa.captures") or []
    min_captures = 3 if asset_type in SHADER_ASSETS else 1
    capture_ok = isinstance(captures, list) and len(captures) >= min_captures and all(
        isinstance(item, dict) and item.get("camera") and HASH_RE.fullmatch(str(item.get("sha256", ""))) and item.get("passed") is True
        for item in captures
    )
    check("visual_qa", capture_ok, f"visual_qa needs at least {min_captures} passed fixed-camera captures with SHA-256 evidence")

    # A declared digest is a claim, not evidence, until something re-hashes the
    # file. With a capture root supplied the claim becomes checkable; without one
    # the result says so plainly rather than letting a reader assume it happened.
    if capture_root is not None:
        capture_failures = verify_captures(captures if isinstance(captures, list) else [], capture_root)
        check("capture_hashes_verified", not capture_failures,
              "; ".join(capture_failures) or "capture digests could not be verified")
        hashes_verified = not capture_failures

    provenance = data.get("provenance", [])
    check("provenance", isinstance(provenance, list) and provenance and all(item.get("source") and item.get("license") for item in provenance if isinstance(item, dict)) and all(isinstance(item, dict) for item in provenance), "every source asset needs source and license provenance")

    if asset_type in SHADER_ASSETS:
        check("geometry", all(_at(data, f"geometry.{field}") is True for field in ("lods", "uv_validated", "tangent_basis_validated", "texel_density_validated")), "geometry LOD, UV, tangent, and texel-density evidence must pass")
        materials = data.get("materials", [])
        required_channels = {"base_color", "roughness", "normal", "metallic_or_specular"}
        material_ok = isinstance(materials, list) and materials and all(
            isinstance(item, dict)
            and item.get("name")
            and required_channels.issubset(set(item.get("channels", [])))
            and item.get("neutral_light_review") is True
            for item in materials
        )
        check("materials", material_ok, "each material needs core PBR channels and a neutral-light review")
        check("lighting", _at(data, "lighting.motivated_key") is True and _at(data, "lighting.exposure_tested") is True and _at(data, "lighting.contact_shadow_tested") is True, "motivated lighting, exposure, and contact-shadow tests must pass")

        required_backends = set(_at(data, "targets.shader_backends") or [])
        shaders = data.get("shaders", [])
        covered: set[str] = set()
        shader_ok = isinstance(shaders, list) and shaders and bool(required_backends)
        for shader in shaders if isinstance(shaders, list) else []:
            if not isinstance(shader, dict) or not shader.get("name") or shader.get("fallback_tested") is not True or shader.get("nan_inf_guards") is not True:
                shader_ok = False
                continue
            for result in shader.get("compile_results", []):
                if not isinstance(result, dict):
                    shader_ok = False
                    continue
                backend = str(result.get("backend", ""))
                if result.get("status") != "passed" or not HASH_RE.fullmatch(str(result.get("artifact_sha256", ""))):
                    shader_ok = False
                else:
                    covered.add(backend)
        check("shader_compilation", shader_ok and required_backends.issubset(covered), "every target shader backend needs passed compiler evidence, artifact SHA-256, guards, and a tested fallback")

        # Same weakness the captures had: `artifact_sha256` was only ever matched
        # against a 64-hex regex, so a manifest could claim every backend compiled
        # and produce nothing. Verified on the same terms as captures when a root
        # is supplied.
        if capture_root is not None:
            shader_failures = verify_shader_artifacts(
                shaders if isinstance(shaders, list) else [], capture_root
            )
            check("shader_artifacts_verified", not shader_failures,
                  "; ".join(shader_failures) or "shader artifacts could not be verified")
            hashes_verified = hashes_verified and not shader_failures

        tiers = data.get("quality_tiers", {})
        measurements = data.get("performance", {}).get("measurements", {}) if isinstance(data.get("performance"), dict) else {}
        tiers_ok = all(isinstance(tiers.get(tier), dict) and tiers[tier] for tier in ("high", "medium", "low"))
        perf_ok = True
        for tier in ("high", "medium", "low"):
            result = measurements.get(tier, {}) if isinstance(measurements, dict) else {}
            required_numbers = ("gpu_p95_ms", "gpu_budget_ms", "memory_mb", "memory_budget_mb", "fps_p1", "fps_min")
            if not isinstance(result.get("hardware"), str) or not result["hardware"].strip() or not all(isinstance(result.get(key), (int, float)) for key in required_numbers):
                perf_ok = False
                continue
            perf_ok &= result["gpu_p95_ms"] <= result["gpu_budget_ms"] and result["memory_mb"] <= result["memory_budget_mb"] and result["fps_p1"] >= result["fps_min"]
        check("quality_tiers", tiers_ok, "high, medium, and low quality tiers need explicit settings")
        check("measured_performance", perf_ok, "each tier needs passing p95 GPU, memory, and p1 FPS measurements on named target hardware")

    if asset_type in SHADER_ASSETS | {"motion"}:
        check("motion", _at(data, "motion.interruptible_states_tested") is True and bool(_at(data, "motion.states")), "motion assets need named states and interruptibility evidence")

    release = data.get("release", {})
    release_ok = (
        isinstance(release, dict)
        and release.get("accepted") is True
        and release.get("creator")
        and release.get("reviewer")
        and release.get("creator") != release.get("reviewer")
        and release.get("acceptance_test")
    )
    check("independent_acceptance", release_ok, "an independent reviewer must accept an executable release test")
    check("no_placeholders", FORBIDDEN_RE.search(json.dumps(data, sort_keys=True)) is None, "manifest contains TODO/placeholder/stub language")
    return {"pass": not failures, "checks": checks, "failures": failures,
            "asset_id": data.get("asset_id"), "asset_type": asset_type,
            # Explicit, always present: a reader must never have to infer whether
            # the digests in this manifest were checked or merely well-formed.
            "hashes_verified": hashes_verified}


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate an AAA graphics evidence manifest")
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--verify-captures", type=Path, metavar="ROOT",
                        help="re-hash every declared capture against files under ROOT; "
                             "without this, digests are only checked for shape")
    args = parser.parse_args()
    try:
        data = json.loads(args.manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"pass": False, "failures": [f"manifest_read_error: {exc}"]}, indent=2))
        return 2
    result = validate(data if isinstance(data, dict) else {}, args.verify_captures)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
