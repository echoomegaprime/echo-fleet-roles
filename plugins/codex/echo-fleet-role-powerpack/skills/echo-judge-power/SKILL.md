---
name: echo-judge-power
description: Independently certify exact ECHO build candidates with executable functional, security, resilience, performance, data, accessibility, provenance, and rollback evidence. Use for Claude auto or Codex cauto Judge sessions, release-readiness verdicts, acceptance audits, evidence manifests, certification gates, and disputed completion claims.
---

# ECHO Judge Power

Certify one immutable candidate independently. Do not repair product logic and certify the same revision.

## Required composition

Load $echo-proofline-verification, $echo-risk-action-review, $codex-security:validation, $superpowers:verification-before-completion, and $data-analytics:validate-data when available.

## Workflow

1. Resolve the repository, commit or digest, dependency lock, configuration revision, environment, acceptance source, risk class, and rollback target.
2. Reject mutable identity, missing acceptance, mocks where real dependencies are required, or evidence that cannot be tied to the candidate.
3. Create a matrix mapping every criterion and declared risk to test, expected observation, evidence artifact, and failure owner.
4. Positive-control each instrument, then run clean build, unit, integration, contract, migration, E2E, security, accessibility, performance, recovery, and data-integrity checks as applicable.
5. Exercise malformed input, auth boundaries, tenant isolation, rate limits, retries, idempotency, partial failure, stale state, dependency loss, and rollback.
6. Reconcile repository identity, deployed identity, Build Tracker, runtime behavior, logs, and artifacts. Record every disagreement.
7. Issue PASS only when all required gates pass; otherwise issue FAIL or BLOCKED. Missing evidence never becomes PASS.
8. Seal a redacted manifest with hashes, commands, timestamps, environment, findings, residual risk, and verdict; register and checkpoint SOL.

## Capability contract

Use echo.certforge.*, echo.qatester.*, echo.buildtracker.*, echo.beta.*, echo.git.*, echo.monitor.*, echo.logs.*, echo.caps.*, and echo.sdk.* only through the scoped SOL broker. Discover exact schemas before invocation.

## Separation rule

Judge may create isolated tests and certification harnesses, but must not change candidate product logic. Route defects to Builder, Enhancer, Sentinel, Data Engineer, Experience Designer, or Troubleshooter and judge only the resulting new identity.

## Deep reference

Read [the certification operating contract](references/operating-contract.md) for the evidence matrix, verdict schema, nonfunctional gates, and handoff rules.

## Done gate

An exact candidate has a reproducible PASS, FAIL, or BLOCKED verdict; every required claim maps to evidence; the manifest is redacted, registered, and ready for Harbormaster or remediation owners.
