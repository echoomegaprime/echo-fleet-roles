---
name: echo-observer-power
description: Monitor ECHO services, diagnose anomalies, repair bounded failures, and harden recurrence controls. Use for Claude auto or Codex cauto observer sessions, uptime watch, drift detection, incident response, or health verification.
---

# ECHO Observer Power

Maintain a live, evidence-backed operational picture and restore degraded systems with minimal blast radius.

## Required composition

Load `$echo-frontier-infrastructure`, `$echo-mcp-incident-recovery`, `$echo-proofline-verification`, and `$superpowers:systematic-debugging`.

## Observe and recover loop

1. Read the observer role, retrieve active dispatches, then capture node, service, queue, dependency, storage, and GPU health.
2. Compare current state with declared invariants and recent healthy baselines. Distinguish transient noise from sustained degradation.
3. For each anomaly, state one hypothesis, supporting evidence, falsification test, exact bounded change, rollback, and expected result.
4. Apply one change at a time. Use staging or an isolated verification path when production exposure is possible.
5. Re-run health, functional smoke, logs, and downstream dependency checks. Roll back immediately on regression.
6. Add the smallest durable guard: alert, timeout, retry boundary, circuit breaker, runbook, or regression test.
7. Register the repair, persist incident learning, checkpoint SOL, and resume monitoring.

## Capability contract

Use `echo.monitor.*`, `echo.node.*`, `echo.logs.*`, `echo.logaggregator.*`, `echo.shell.*`, and authorized `echo.crucible.*` through the scoped broker. Discover exact cap schemas and service-specific control routes first; never depend on static node IPs.

## Proof gate

Recovery requires before/after evidence, a functional check beyond process state, downstream validation, and recurrence protection. A restarted process alone is not a verified fix.
