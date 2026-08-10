"""Tests for capture-digest verification in the AAA asset gate.

The gate previously accepted any 64-hex string as a capture digest, so a manifest
asserting `"a"*64` passed. These lock in that a forged digest fails, a real one
passes, a manifest cannot steer the gate into hashing files outside the capture
root, and that an unverified run says so rather than implying it checked.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import aaa_asset_gate as gate  # noqa: E402

FAKE = "a" * 64


def _fixture(tmp_path: Path, digest: str, rel: str) -> tuple[dict, Path]:
    captures = tmp_path / "caps"
    captures.mkdir(exist_ok=True)
    payload = b"real capture bytes\n"
    (captures / "front.png").write_bytes(payload)
    manifest = {"visual_qa": {"captures": [
        {"camera": "front", "sha256": digest, "passed": True, "path": rel}
    ]}}
    return manifest, tmp_path


def _real_digest(tmp_path: Path) -> str:
    return hashlib.sha256((tmp_path / "caps" / "front.png").read_bytes()).hexdigest()


def test_forged_digest_is_rejected(tmp_path: Path) -> None:
    """64 valid hex characters that do not match the file must fail."""
    manifest, root = _fixture(tmp_path, FAKE, "caps/front.png")
    result = gate.validate(manifest, root)
    assert result["checks"]["capture_hashes_verified"] is False
    assert result["hashes_verified"] is False
    assert any("digest mismatch" in f for f in result["failures"]), result["failures"]


def test_real_digest_verifies(tmp_path: Path) -> None:
    """Positive control — without it, 'everything fails' would look like a fix."""
    manifest, root = _fixture(tmp_path, FAKE, "caps/front.png")
    manifest["visual_qa"]["captures"][0]["sha256"] = _real_digest(root)
    result = gate.validate(manifest, root)
    assert result["checks"]["capture_hashes_verified"] is True
    assert result["hashes_verified"] is True


def test_path_traversal_is_refused(tmp_path: Path) -> None:
    """A manifest must not be able to make the gate hash arbitrary files."""
    manifest, root = _fixture(tmp_path, FAKE, "../../../../etc/passwd")
    result = gate.validate(manifest, root)
    assert result["checks"]["capture_hashes_verified"] is False
    assert any("escapes the verification root" in f or "does not exist" in f
               for f in result["failures"]), result["failures"]


def test_missing_path_is_not_silently_accepted(tmp_path: Path) -> None:
    """A digest with no file cannot be verified, and must not pass as if it were."""
    manifest, root = _fixture(tmp_path, FAKE, "caps/front.png")
    del manifest["visual_qa"]["captures"][0]["path"]
    result = gate.validate(manifest, root)
    assert result["checks"]["capture_hashes_verified"] is False
    assert any("no 'path'" in f for f in result["failures"]), result["failures"]


def test_absent_file_fails(tmp_path: Path) -> None:
    manifest, root = _fixture(tmp_path, FAKE, "caps/nope.png")
    result = gate.validate(manifest, root)
    assert any("does not exist" in f for f in result["failures"]), result["failures"]


def test_unverified_run_declares_itself(tmp_path: Path) -> None:
    """Without a capture root the gate must NOT imply it checked anything."""
    manifest, _ = _fixture(tmp_path, FAKE, "caps/front.png")
    result = gate.validate(manifest)
    assert result["hashes_verified"] is False
    assert "capture_hashes_verified" not in result["checks"]


def test_hashes_verified_is_always_present() -> None:
    """A consumer must never have to infer whether digests were checked."""
    assert "hashes_verified" in gate.validate({})


def test_digest_matches_hashlib(tmp_path: Path) -> None:
    """Guard the hashing itself, including the chunked read path."""
    blob = tmp_path / "big.bin"
    blob.write_bytes(b"x" * (gate.READ_CHUNK + 1234))
    assert gate._digest(blob) == hashlib.sha256(blob.read_bytes()).hexdigest()


def test_gate_cli_accepts_verify_flag(tmp_path: Path, capsys, monkeypatch) -> None:
    """End-to-end through main(): a forged manifest exits non-zero."""
    manifest, root = _fixture(tmp_path, FAKE, "caps/front.png")
    path = tmp_path / "m.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    monkeypatch.setattr(sys, "argv",
                        ["aaa_asset_gate.py", str(path), "--verify-captures", str(root)])
    assert gate.main() == 2
    assert json.loads(capsys.readouterr().out)["hashes_verified"] is False


# --- shader compile artifacts: the same self-asserted weakness as captures ----

def _shader_manifest(digest: str, rel: str) -> dict:
    return {
        "asset_type": "game",
        "targets": {"shader_backends": ["glsl"]},
        "shaders": [{
            "name": "hero_surface",
            "fallback_tested": True,
            "nan_inf_guards": True,
            "compile_results": [
                {"backend": "glsl", "status": "passed",
                 "artifact_sha256": digest, "path": rel}
            ],
        }],
    }


def _shader_fixture(tmp_path: Path) -> str:
    artifacts = tmp_path / "shaders"
    artifacts.mkdir(exist_ok=True)
    blob = artifacts / "hero_surface.glsl.bin"
    blob.write_bytes(b"compiled shader bytes\n")
    return hashlib.sha256(blob.read_bytes()).hexdigest()


def test_forged_shader_artifact_is_rejected(tmp_path: Path) -> None:
    """A manifest could claim every backend compiled and produce nothing."""
    _shader_fixture(tmp_path)
    result = gate.validate(_shader_manifest(FAKE, "shaders/hero_surface.glsl.bin"), tmp_path)
    assert result["checks"]["shader_artifacts_verified"] is False
    assert result["hashes_verified"] is False
    assert any("digest mismatch" in f for f in result["failures"]), result["failures"]


def test_real_shader_artifact_verifies(tmp_path: Path) -> None:
    """Positive control for the shader path."""
    real = _shader_fixture(tmp_path)
    result = gate.validate(_shader_manifest(real, "shaders/hero_surface.glsl.bin"), tmp_path)
    assert result["checks"]["shader_artifacts_verified"] is True


def test_shader_artifact_traversal_is_refused(tmp_path: Path) -> None:
    real = _shader_fixture(tmp_path)
    result = gate.validate(_shader_manifest(real, "../../../../etc/passwd"), tmp_path)
    assert result["checks"]["shader_artifacts_verified"] is False
    assert any("escapes the verification root" in f or "does not exist" in f
               for f in result["failures"]), result["failures"]


def test_shader_compile_claim_without_a_path_fails(tmp_path: Path) -> None:
    """Declaring a digest with no file is a claim, not evidence."""
    real = _shader_fixture(tmp_path)
    manifest = _shader_manifest(real, "shaders/hero_surface.glsl.bin")
    del manifest["shaders"][0]["compile_results"][0]["path"]
    result = gate.validate(manifest, tmp_path)
    assert result["checks"]["shader_artifacts_verified"] is False
    assert any("no 'path'" in f for f in result["failures"]), result["failures"]


def test_shader_with_no_compile_results_is_flagged(tmp_path: Path) -> None:
    real = _shader_fixture(tmp_path)
    manifest = _shader_manifest(real, "shaders/hero_surface.glsl.bin")
    manifest["shaders"][0]["compile_results"] = []
    result = gate.validate(manifest, tmp_path)
    assert any("no compile_results" in f for f in result["failures"]), result["failures"]


def test_captures_and_shaders_share_one_confinement_check() -> None:
    """Both paths must route through _verify_one, or one copy drifts."""
    import inspect
    for fn in (gate.verify_captures, gate.verify_shader_artifacts):
        assert "_verify_one" in inspect.getsource(fn), fn.__name__
