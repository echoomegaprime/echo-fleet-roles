---
name: echo-beta-power
description: Battle-test ECHO products through realistic user journeys, evidence capture, and regression-ready findings. Use for Claude auto or Codex cauto beta sessions, release qualification, exploratory testing, or beta objective verification.
---

# ECHO Beta Power

Test what a real user experiences, across happy paths, edge cases, degraded dependencies, accessibility, performance, and recovery.

## Required composition

Load `$browser-automation`, `$echo-proofline-verification`, `$echo-delivery-evidence`, and `$data-analytics:validate-data` when relevant.

## Beta loop

1. Resolve the live or staging target, release identity, persona, supported environments, and acceptance criteria.
2. Verify the URL or executable is reachable before creating a beta objective or claiming testability.
3. Design journeys that cover onboarding, core value, invalid input, empty state, permissions, persistence, refresh, failure, and recovery.
4. Execute in a clean isolated session while capturing timestamps, screenshots, network or console evidence, build identity, and exact reproduction steps.
5. Triage by user impact and reproducibility. Distinguish product defects, environment faults, test-data problems, and unclear requirements.
6. Re-test fixes from the original reproduction, then run adjacent regression journeys.
7. Update the beta objective truthfully, register results, persist recurring failure patterns, and continue until the release gate is resolved.

## Capability contract

Use `claude.shadowglass.*`, `echo.beta.*`, `echo.website.*`, and `echo.sentinel.*` through the scoped broker. Reserve a dedicated browser tab and never expose protected fields or session secrets.

## Proof gate

Pass requires a real journey on the declared build and target, not an HTTP 200 alone. Failures require deterministic reproduction evidence; fixes require a clean re-test and adjacent regression coverage.
