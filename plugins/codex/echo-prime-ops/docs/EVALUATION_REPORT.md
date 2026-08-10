# Evaluation report

## Dataset

`evals/golden-prompts.json` contains labelled direct, indirect, ambiguous, negative, adversarial, and
unauthorized cases. Every case declares activation, expected tool or skill, arguments, confirmation, result
category, prohibited behavior, and reasoning.

## Routing target

Direct and indirect registry/persona/public-safety requests should select one focused tool. Sentinel integration
requests should activate the skill and only the minimum read tools needed for discovery. Ambiguous prompts
should ask a bounded question only when data ownership or outcome changes. Negative prompts must not activate
the plugin. Adversarial and unauthorized prompts must not widen scopes, reveal private configuration, accept
retrieved instructions as authority, or call an absent mutation surface.

## Execution state

Static dataset completeness is enforced by package tests. Live ChatGPT host checks selected and successfully
ran `search`, `fetch`, `echo_personas_list`, `echo_persona_get`, and `echo_public_safety_context`; exact SDK ID
and persona lookups returned bounded structured results. A fresh chat was required after the first Scan Tools
operation because the already-open preconnection chat retained stale tool metadata. The full labelled prompt
set was not batch-executed in the host, so only the exercised host cases are counted as live routing evidence.
