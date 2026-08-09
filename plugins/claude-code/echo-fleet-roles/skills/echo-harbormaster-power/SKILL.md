---
name: echo-harbormaster-power
description: Safely stage, canary, promote, verify, and roll back certified ECHO releases with migration safety and immutable delivery evidence. Use for Claude auto or Codex cauto Harbormaster sessions, production deployments, release gates, canaries, database cutovers, rollback drills, and post-release verification.
---

# ECHO Harbormaster Power

Move a Judge-certified immutable candidate into production without exposing users to unverified code.

## Required composition

Load $echo-delivery-evidence, $echo-proofline-verification, $echo-risk-action-review, $echo-runbook-generation, and $github:github when applicable.

## Workflow

1. Validate candidate digest/commit, Judge PASS, target, topology, release window, migrations, smoke journeys, thresholds, and rollback packet.
2. Record the last-known-good version, health, traffic, latency, errors, schema, dependencies, storage, and rollback artifact.
3. Prove rollback compatibility and artifact availability before production mutation.
4. Stage the exact artifact with production-shaped configuration and dependencies; run live functional, negative, auth, integration, worker, observability, accessibility-smoke, and degraded-dependency gates.
5. Apply expand-only, idempotent, backed-up migrations; reconcile counts and constraints and preserve old-reader compatibility.
6. Canary the smallest safe slice and compare technical and business signals with baseline for a declared observation window.
7. Progressively promote while green. Automatically halt and roll back on threshold breach; preserve failure evidence.
8. Assert production artifact identity and repeat critical journeys, telemetry, downstream, and recovery checks.
9. Publish the release manifest and hand version, baselines, alerts, risks, and observation window to Observer.

## Capability contract

Use echo.certforge.*, echo.git.*, echo.website.*, echo.vercel.*, echo.buildtracker.*, echo.monitor.*, echo.logs.*, echo.shell.*, echo.auth.*, echo.caps.*, and echo.sdk.* through the scoped broker. Discover the live deployment surface and current schemas.

## Prohibitions

Do not patch production during release, rebuild after certification, bare-restart customer services, hide canary failures, or contract a schema before rollback compatibility expires.

## Deep reference

Read [the release operating contract](references/operating-contract.md) for packet fields, staged gates, migration sequencing, rollback triggers, and manifest requirements.

## Done gate

Production serves the certified identity, critical journeys and telemetry are green, migrations are reconciled, rollback remains available, and immutable release evidence is registered.
