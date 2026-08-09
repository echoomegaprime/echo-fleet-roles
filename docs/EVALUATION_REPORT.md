# Evaluation Report

The role evaluation set covers direct and indirect role activation, ambiguity, negative prompts, malformed input, unauthorized operations, destructive-action boundaries, and prompt injection. Structural validation ensures every expected role resolves through the canonical registry and every prohibited behavior retains its boundary.

Results:

- Golden cases: 60.
- Category contract: PASS.
- Expected role resolution: PASS for every activating case.
- Unknown-role rejection: PASS.
- Runtime transition and hook propagation: PASS.
- Live host language-model routing: evaluated during exact-commit E2E and recorded as release evidence, not inferred from static tests.
