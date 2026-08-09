---
name: echo-architect-power
description: Design ECHO systems, ADRs, threat models, interfaces, and acceptance-gated build phases. Use for Claude auto or Codex cauto architect sessions, cross-module design, migration planning, or builder-ready specifications.
---

# ECHO Architect Power

Turn objectives into implementable, observable, secure system contracts. Reuse existing ECHO patterns before introducing abstractions.

## Required composition

Load `$echo-graph-mode`, `$echo-runbook-generation`, `$echo-risk-action-review`, and `$codex-security:threat-model` when applicable.

## Architecture loop

1. Inspect the existing system, nearest instructions, live capability surface, Arcanum templates, code library, and current documentation.
2. Define context, constraints, invariants, trust boundaries, data ownership, failure modes, and non-goals.
3. Compare viable options with operational cost, reversibility, security, compatibility, and migration risk.
4. Select a design and record an ADR with explicit consequences and rollback.
5. Split implementation into independently shippable phases. Give every phase real acceptance tests, observability, and evidence requirements.
6. Validate the design against current capabilities and repository reality; remove guessed endpoints, models, flags, and schemas.
7. Register and persist the architecture decision, then hand builders an executable contract.

## Capability contract

Use the role registry scopes. Discover with `echo.caps.*` and `echo.sdk.*`; search reusable functions through `echo.functions.*`; inspect engine and swarm surfaces only when the design needs them. Invoke all moving ECHO state through the scoped SOL broker.

## Proof gate

An architecture is complete only when its interfaces, dependency versions, threat boundaries, phase tests, rollback, ownership, and live capability assumptions are all explicit and independently checkable.
