# AAA Evidence Contract

`aaa_asset_gate.py` accepts one JSON object. The required top-level fields are:

- `schema_version: 1`, `asset_id`, and `asset_type` (`interactive-3d`, `game`, `web-3d`, `motion`, or `static`).
- `art_direction`, `color`, `accessibility`, `visual_qa`, `provenance`, and `release` for every asset.
- `geometry`, `materials`, `lighting`, `targets.shader_backends`, `shaders`, `quality_tiers`, and per-tier `performance.measurements` for shader-bearing assets.
- `motion.states` and `motion.interruptible_states_tested` for animated or interactive assets.

Every capture and compiled shader artifact is identified by a 64-character SHA-256. High, medium, and low tiers each report measured p95 GPU frame time, GPU budget, memory, memory budget, p1 FPS, and minimum FPS on named target hardware. Release acceptance must name different creator and reviewer identities and the executable acceptance test.

Backend names are project-defined but should be exact compiler targets such as `dx12-sm6`, `vulkan-spirv`, `metal-msl`, `webgpu-wgsl`, `unreal-sm6`, `unity-urp`, or `godot-vulkan`. A generic “compiled” flag is not sufficient.

Run:

```powershell
python scripts/aaa_asset_gate.py path\to\aaa-evidence.json
```

Exit `0` means every applicable contract check passed. Exit `2` means the claim is blocked and the JSON output lists exact gaps.
