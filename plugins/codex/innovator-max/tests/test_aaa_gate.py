from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN_ROOT / "skills" / "aaa-graphics-pipeline" / "scripts"))

from aaa_asset_gate import validate  # noqa: E402

H = "a" * 64


def valid_manifest():
    measurements = {tier: {"hardware": "target-gpu", "gpu_p95_ms": 12, "gpu_budget_ms": 16.6, "memory_mb": 800, "memory_budget_mb": 1024, "fps_p1": 60, "fps_min": 55} for tier in ("high", "medium", "low")}
    return {
        "schema_version": 1,
        "asset_id": "hero-scene",
        "asset_type": "interactive-3d",
        "art_direction": {"brief": "cinematic focal scene", "palette": ["#000", "#d4af37"], "focal_hierarchy": ["hero", "cta"], "references": ["approved-board-1"]},
        "color": {"working_space": "ACEScg", "display_space": "sRGB", "tone_mapper": "ACES", "hdr_sdr_tested": True},
        "accessibility": {"reduced_motion": True, "color_vision": True, "contrast": True},
        "visual_qa": {"captures": [{"camera": f"cam-{i}", "sha256": H, "passed": True} for i in range(3)]},
        "provenance": [{"source": "authored", "license": "proprietary"}],
        "geometry": {"lods": True, "uv_validated": True, "tangent_basis_validated": True, "texel_density_validated": True},
        "materials": [{"name": "metal", "channels": ["base_color", "roughness", "normal", "metallic_or_specular"], "neutral_light_review": True}],
        "lighting": {"motivated_key": True, "exposure_tested": True, "contact_shadow_tested": True},
        "targets": {"shader_backends": ["dx12-sm6", "vulkan-spirv"]},
        "shaders": [{"name": "hero", "fallback_tested": True, "nan_inf_guards": True, "compile_results": [{"backend": backend, "status": "passed", "artifact_sha256": H} for backend in ("dx12-sm6", "vulkan-spirv")]}],
        "quality_tiers": {tier: {"resolution_scale": scale} for tier, scale in (("high", 1), ("medium", .8), ("low", .6))},
        "performance": {"measurements": measurements},
        "motion": {"states": ["idle", "focus"], "interruptible_states_tested": True},
        "release": {"accepted": True, "creator": "builder", "reviewer": "beta", "acceptance_test": "render-qa --all-tiers"},
    }


class AaaEvidenceTests(unittest.TestCase):
    def test_valid_shader_asset_passes(self):
        result = validate(valid_manifest())
        self.assertTrue(result["pass"], result["failures"])

    def test_missing_backend_and_self_review_fail(self):
        data = copy.deepcopy(valid_manifest())
        data["shaders"][0]["compile_results"].pop()
        data["release"]["reviewer"] = "builder"
        result = validate(data)
        self.assertFalse(result["pass"])
        self.assertFalse(result["checks"]["shader_compilation"])
        self.assertFalse(result["checks"]["independent_acceptance"])

    def test_unnamed_performance_hardware_fails(self):
        data = copy.deepcopy(valid_manifest())
        data["performance"]["measurements"]["high"]["hardware"] = ""
        result = validate(data)
        self.assertFalse(result["pass"])
        self.assertFalse(result["checks"]["measured_performance"])


if __name__ == "__main__":
    unittest.main()
