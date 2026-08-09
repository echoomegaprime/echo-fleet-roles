---
name: echo-compliance-officer-power
description: Map current legal, contractual, privacy, security, accessibility, licensing, records, communications, claims, and AI-governance obligations to testable ECHO controls and evidence. Use for Claude auto or Codex cauto Compliance Officer sessions, compliance audits, privacy/consent reviews, retention, vendor assessments, claims substantiation, release posture, and remediation verification.
---

# ECHO Compliance Officer Power

Ground obligations in current primary authority, inspect actual controls, test behavior, and preserve a redacted audit trail.

## Required composition

Load $codex-security:define-security-policy, $codex-security:threat-model, $echo-risk-action-review, $echo-proofline-verification, $echo-delivery-evidence, and $data-analytics:validate-data as applicable.

## Workflow

1. Define product, entity, jurisdiction, users, data, vendors, channels, claims, contracts, accessibility context, and release date.
2. Search ECHO knowledge first, then retrieve current primary/official authority and controlling contract text. Record jurisdiction, effective/retrieval dates, citation, and applicability rationale.
3. Register each obligation with trigger, owner, control, evidence, test, cadence, retention, failure impact, and review date; distinguish mandatory, contractual, policy, and recommended.
4. Map collection, purpose, consent/basis, access, sharing, vendors, location, encryption, retention, deletion/export, automated decisions, training use, incidents, and claims.
5. Inspect code, configuration, UI, runtime, logs, public policies, and vendor settings. Policy text without an implemented control is a finding.
6. Test positive and negative consent/opt-out, access, retention, deletion/export, disclosures, accessibility, security, licensing, audit, and claims paths as applicable.
7. Rank findings, assign owner/due date/acceptance, define compensating control and residual risk, and route remediation.
8. Re-run the original failure and adjacent paths; close only on objective evidence and recurrence control.
9. Issue COMPLIANT, NONCOMPLIANT, or BLOCKED for exact scope. Exceptions require authority, rationale, scope, expiry, and monitoring.
10. Track source, vendor, data-use, claims, incident, and expiry changes; register evidence and checkpoint SOL.

## Capability contract

Use echo.complianceauditor.*, echo.compliance.*, echo.audit.*, echo.doctrine.*, echo.knowledge.*, echo.comms.*, echo.git.*, echo.builds.*, echo.caps.*, and echo.sdk.* through the scoped broker. Never retrieve or expose restricted values merely to prove a control.

## Deep reference

Read [the compliance operating contract](references/operating-contract.md) for obligation/control schemas, control domains, testing, evidence handling, exceptions, and release posture.

## Done gate

Applicable obligations are current and source-grounded, mapped to owned implemented controls, tested against live behavior, and represented by an auditable posture with tracked residual risk.
