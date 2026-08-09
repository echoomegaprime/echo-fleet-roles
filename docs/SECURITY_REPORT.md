# Security Report

A complete offline Codex Security scan reviewed the pre-commit repository snapshot across registry parsing, SQLite state, CLI input, lifecycle hooks, automation, CI, plugin content, and public-data boundaries.

- Coverage: complete, all 189 tracked source and configuration files, including hidden marketplace and CI files.
- Reportable findings: 0.
- Hardenings applied before finalization: explicit connection closing on Windows; idempotency-key intent binding; URI-safe read-only hook paths; immutable GitHub Actions SHAs; strict public-path and private-literal tests.
- Independent delegated baseline: unavailable under the active no-delegation task mode; the complete audit ran sequentially.

The canonical scan manifest, findings, coverage, and generated report are shipped as exact release evidence with their hashes.
