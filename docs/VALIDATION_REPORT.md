# Validation Report

## Local gates

| Gate | Status | Evidence |
| --- | --- | --- |
| JSON and manifest parsing | PASS | `scripts/validate_plugins.py` |
| Registry contract | PASS | exact 30 roles; no private boot paths or plugin overrides |
| Runtime unit tests | PASS | default, persistence, fencing, idempotency, audited no-op |
| CLI tests | PASS | validate, switch, and invalid-role failure |
| Hook tests | PASS | both supported events plus fail-open behavior |
| Host parity and privacy tests | PASS | 30 roles + control skill on both hosts; private literals absent |
| Same-session smoke | PASS | commander to reverse-engineer without process restart |
| Codex plugin validator | PASS | current local validator |

## Release gates

Hosted CI, FORGE E2E, Cert Forge, GitHub App Suite conformance, release integrity, and ANVIL canonical clone are exact-commit gates. Their immutable identifiers belong in release assets and the GitHub release, not in this pre-certification source snapshot.
