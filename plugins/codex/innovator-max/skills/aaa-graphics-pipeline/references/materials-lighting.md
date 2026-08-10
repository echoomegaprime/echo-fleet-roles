# Materials and lighting playbook

## Material passes

1. Validate silhouette and scale under neutral gray lighting.
2. Set base color and roughness from the intended real-world material family.
3. Add directional response only when motivated: normal, anisotropy, clearcoat, transmission, or subsurface.
4. Add macro variation before micro noise.
5. Add contact, wear, dirt, and edge response through authored masks—not uniform random grunge.
6. Recheck under three lighting conditions and a low-exposure view.

## Lighting passes

1. Composition: establish focal hierarchy and silhouette separation.
2. Key: define form and direction.
3. Fill/bounce: preserve readable shadow detail.
4. Rim/practicals: separate layers and support narrative motivation.
5. Atmosphere: depth cues, fog, volumetrics, reflections.
6. Grade: exposure, contrast, saturation, highlight rolloff, and display transform.

## Common defects

- Flatness: missing roughness variation, contact shadows, or scale cues.
- Plastic look: excessive specular, uniform roughness, and weak micro-normal breakup.
- Muddy image: low-frequency contrast lost to fog, bloom, or crushed blacks.
- Toy-like image: incorrect scale, sharp edges, or unmotivated lighting.
- Temporal shimmer: undersampled detail, unstable reflections, or unsuitable mip/LOD transitions.
