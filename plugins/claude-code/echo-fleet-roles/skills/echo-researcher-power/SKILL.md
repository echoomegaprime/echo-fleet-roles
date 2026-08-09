---
name: echo-researcher-power
description: Produce current, source-grounded research with corroboration, uncertainty, and actionable conclusions. Use for Claude auto or Codex cauto researcher sessions, technical investigation, vendor comparison, emerging facts, or evidence briefs.
---

# ECHO Researcher Power

Turn an open question into decision-grade evidence. Retrieve current facts and separate primary evidence, secondary analysis, inference, and unknowns.

## Required composition

Load `$echo-ragops`, `$echo-proofline-verification`, and `$browser-automation`; load a domain-specific skill when available.

## Research loop

1. Define the decision, scope, date sensitivity, evidence standard, and stopping criteria.
2. Search ECHO memory and Knowledge Forge first. For moving or missing facts, use official primary sources and ingest durable findings when authorized.
3. Build an evidence ledger containing claim, source, date, authority, direct support, conflicts, and confidence.
4. Corroborate material claims across independent sources when possible. Treat search snippets, index hits, and model output as leads rather than proof.
5. Analyze alternatives, quantify uncertainty, identify disconfirming evidence, and state what would change the conclusion.
6. Deliver the recommendation first, with citations adjacent to claims and a compact record of unresolved unknowns.
7. Persist reusable research and checkpoint the role loop.

## Capability contract

Use `echo.grok.*`, `echo.swarm.*`, `echo.knowledge.*`, `echo.library.*`, `echo.caps.*`, and `claude.shadowglass.*` through the scoped broker. Browser automation must use a dedicated tab and preserve authenticated session boundaries.

## Proof gate

Every decisive claim needs directly supporting evidence. Mark inferences as inferences, include dates for moving facts, and never promote absence of evidence into a verified negative.
