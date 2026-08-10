# Shader performance and quality tiers

Track per-material and per-pass: instruction count, texture samples, dependent reads, branches, precision, overdraw, render-target cost, shader variant count, and GPU milliseconds.

Budgets are project-specific. Establish a baseline on target hardware, then record the relative cost and demonstrated visual gain of every change. Never invent a universal limit.

Tier down in this order when needed: post effects, volumetrics, reflection quality, shadow resolution/filtering, particle count, material secondary layers, texture resolution, then geometry detail. Preserve silhouette, focal readability, and input feedback as long as possible.

Every fallback must compile and render a deliberate result. A missing feature must degrade to a simpler authored response, not black, magenta, NaN, or an unlit debug state.
