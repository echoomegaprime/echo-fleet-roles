---
name: echo-troubleshooter-power
description: Diagnose ECHO failures systematically, repair root causes, and prove recurrence resistance. Use for cauto troubleshooter sessions, broken tools, services, integrations, builds, or performance regressions.
---

# ECHO Troubleshooter Power

Move from symptom to verified root cause with controlled experiments and one evidence-backed change at a time.

## Required composition

Load `$superpowers:systematic-debugging`, `$echo-mcp-incident-recovery`, `$echo-frontier-infrastructure`, and `$echo-proofline-verification`.

## Troubleshooting loop

1. Capture the exact failure, expected behavior, time window, affected scope, last-known-good state, and reproducible command or journey.
2. Gather logs, metrics, service status, dependency health, configuration identity, version, resource pressure, and recent changes.
3. Localize the failing boundary. State one hypothesis with evidence, a falsification test, exact change, rollback, and expected observation.
4. Run the smallest safe experiment. Do not stack speculative changes or restart unrelated services.
5. Apply the root-cause fix, then reproduce the original scenario and test adjacent failure and recovery paths.
6. Add a regression test, health signal, diagnostic, timeout, or runbook that catches recurrence earlier.
7. Record the timeline, cause, repair, proof, residual risk, and durable learning; checkpoint SOL and continue if another defect remains.

## Capability contract

Use `echo.monitor.*`, `echo.logs.*`, `echo.logaggregator.*`, `echo.shell.*`, `echo.node.*`, `echo.caps.*`, and `echo.sdk.*` through the scoped broker. Discover schemas, service-specific control caps, and node state live.

## Proof gate

Process health or disappearance of one error is insufficient. The original failure must be reproducibly fixed, adjacent behavior must remain green, and recurrence detection must be present.
