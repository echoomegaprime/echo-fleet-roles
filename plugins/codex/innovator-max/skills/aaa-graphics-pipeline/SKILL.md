---
name: aaa-graphics-pipeline
description: Use when creating or upgrading game, web, 3D, motion, or interactive visuals to AAA quality, including physically based materials, lighting, shaders, effects, optimization, accessibility, and visual QA.
---

# AAA Graphics Pipeline

Build visuals as a measurable production system: art direction, physically coherent material response, stable lighting, authored motion, robust shaders, scalable quality tiers, and evidence-based visual QA. AAA means intentional pixels plus stable performance—not merely more effects.

## Quality Bar

- Establish a visual brief: subject, camera, palette, focal hierarchy, mood, references, target platform, resolution, frame rate, and accessibility constraints.
- State the working/display color space and avoid accidental double tone-mapping or gamma-space lighting.
- Use physically based inputs: base color, roughness, metallic/specular, normal, height, ambient occlusion, emission, clearcoat, transmission, and anisotropy only when they describe the surface.
- Make scale, edge treatment, roughness variation, micro-normal detail, and contact shadows agree.
- Light for readability with motivated key/fill/rim sources, controlled contrast, contact/bounce cues, silhouette separation, and deliberate highlights.
- Author motion with anticipation, weight, easing, secondary motion, camera intent, and interruptible state transitions.
- Budget every shader: instruction/texture bandwidth, precision, branches, variants, overdraw, and fallbacks.

## Workflow

1. **Art direction** — write the visual contract and identify what must remain readable at the smallest viewport.
2. **Geometry/UVs** — validate silhouette, topology, tangents, UV padding, texel density, deformation, LODs, and instancing before polish.
3. **Materials** — layer macro shape, primary response, secondary breakup, micro detail, wear, and meaningful masks under neutral and intended lighting.
4. **Lighting/atmosphere** — establish composition and key light first; add bounce, reflections, fog, volumetrics, particles, and post only when each supports depth or focus.
5. **Effects/post** — use bloom, DOF, motion blur, grain, distortion, and chromatic effects sparingly; test HDR, SDR, low brightness, and color-vision differences.
6. **Optimization tiers** — ship high/medium/low tiers with explicit changes to resolution, shadows, reflections, volumetrics, particles, materials, and post; measure target hardware.
7. **Visual QA** — capture fixed cameras and check aliasing, shimmer, seams, z-fighting, leaks, exposure, color, pop-in, animation states, and degraded tiers.

## Shader Gate

Before shipping a shader, confirm coordinate spaces, normalized normals/tangents, valid derivatives, intentional texture formats/mips, deliberate UV wrapping, acceptable transparency sorting, appropriate precision, compiled fallbacks, guarded NaN/Inf paths, and backend coverage.

## AAA Readiness

Do not claim AAA readiness until the artifact has a visual brief, reference captures, coherent materials, motivated lighting, stable motion, compiled shaders, quality tiers, measured performance, visual QA evidence, and deliberate fallbacks. Encode that evidence in a manifest and pass `scripts/aaa_asset_gate.py`; prose review alone cannot close the gate. Report exact gaps.

## Resources

- `references/materials-lighting.md` for material and lighting review.
- `references/shader-performance.md` for shader budgeting and tiering.
- `references/aaa-evidence-contract.md` for the engine-neutral evidence manifest and backend compiler matrix.
- `scripts/visual_budget.py` for numerical budget checks.
- `scripts/aaa_asset_gate.py` for the fail-closed production acceptance gate.
