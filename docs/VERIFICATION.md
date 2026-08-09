# Verification Evidence

This file is populated with immutable exact-commit evidence during the release process. A local result is not a production certificate.

Required gates:

1. Static contract and privacy scan.
2. Unit, CLI, packaging, hook, and same-session switching tests.
3. Codex plugin validator.
4. Hosted GitHub Actions on the exact commit.
5. Real end-to-end role transition on FORGE.
6. Signed Cert Forge `PRODUCTION_READY` certificate for the exact commit.
7. Independent eight-app GitHub App Suite conformance certificate for the exact commit.
8. Immutable release assets with SHA-256 integrity metadata.
9. Clean canonical ANVIL clone and catalog registration.

No gate is recorded as passed until its live evidence exists.
