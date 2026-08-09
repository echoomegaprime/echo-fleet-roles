---
name: echo-steward-power
description: Maintain ECHO storage, backups, repositories, services, capacity, and lifecycle hygiene safely. Use for cauto steward sessions, cleanup, consolidation, backup validation, or resource pressure.
---

# ECHO Steward Power

Preserve operational continuity and recoverability while improving hygiene. Prefer copy-verify-retain or copy-verify-symlink workflows over destructive moves.

## Required composition

Load `$echo-frontier-infrastructure`, `$echo-risk-action-review`, `$echo-runbook-generation`, and `$echo-proofline-verification`.

## Stewardship loop

1. Resolve live node identity, mounts, free space, services, repositories, backups, retention rules, and protected paths.
2. Classify candidates as live, recoverable cache, reproducible artifact, unique data, personal data, or unknown. Unknown is preserved.
3. State expected benefit, exact target, verification method, rollback, and dependent services before mutation.
4. Copy first, verify size and hashes, update consumers, smoke dependent services, then retire originals only when explicitly within scope.
5. Never bulk-delete shared roots, run broad prune operations, or include protected personal data in cleanup.
6. Test restoration, not just backup creation. Validate manifests, encryption, permissions, retention, and off-box readability.
7. Record recovered capacity, retained copies, service checks, rollback, and next maintenance window.

## Capability contract

Use `echo.monitor.*`, `echo.node.*`, `echo.fs.*`, `echo.backup.*`, `echo.git.*`, `echo.logs.*`, `echo.logaggregator.*`, and bounded `echo.shell.*` through the scoped broker. Resolve nodes dynamically and discover service-specific control caps; do not hardcode moving IPs.

## Proof gate

Storage work requires verified target paths, before/after capacity, integrity checks, dependent-service smoke, and a recovery path. A command exit code alone is not evidence of safe stewardship.
