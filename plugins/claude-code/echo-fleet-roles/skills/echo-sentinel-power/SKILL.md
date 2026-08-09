---
name: echo-sentinel-power
description: Defend ECHO systems through continuous security assessment, threat modeling, incident containment, and verified remediation. Use for Claude auto or Codex cauto sentinel sessions, security posture reviews, findings, or defensive operations.
---

# ECHO Sentinel Power

Operate a continuous defensive loop across code, infrastructure, identities, data, dependencies, and runtime behavior. Stay within the authorized ECHO scope and preserve forensic evidence.

## Required composition

Load `$codex-security:security-scan`, `$codex-security:deep-security-scan`, `$codex-security:threat-model`, `$codex-security:track-findings`, `$codex-security:validation`, and `$echo-risk-action-review`.

## Defense loop

1. Retrieve live alerts, asset inventory, exposure, recent changes, service health, and open findings.
2. Establish scope, threat model, critical assets, trust boundaries, attacker paths, and evidence-retention needs.
3. Triage findings by exploitability, impact, exposure, confidence, and remediation cost. De-duplicate before escalating.
4. Validate safely using the least invasive authorized technique. Preserve hashes, timestamps, logs, and reproduction detail.
5. Contain active risk with a bounded reversible change; then fix root cause and add a regression or detection control.
6. Re-test the original path, surrounding controls, service functionality, and monitoring. Reopen any finding lacking proof.
7. Record residual risk, owner, deadline, rollback, verification, and durable lessons.

## Capability contract

Use `echo.crucible.*`, `echo.guardian.*`, `echo.autoshield.*`, `echo.monitor.*`, `echo.logs.*`, `echo.logaggregator.*`, and bounded `echo.shell.*` through the scoped broker. Discover tier, schema, and service-specific control routes before active security operations; never expose secrets or restricted data.

## Proof gate

A finding is closed only when the exploit or failure path is no longer reproducible, the intended service still works, and a durable preventive or detective control is verified.
