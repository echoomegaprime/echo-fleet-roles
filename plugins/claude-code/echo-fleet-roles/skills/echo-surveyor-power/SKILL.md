---
name: echo-surveyor-power
description: Map ECHO systems, repositories, services, data flows, dependencies, drift, and risk from live evidence. Use for Claude auto or Codex cauto surveyor sessions, inventory, topology, readiness, or gap analysis.
---

# ECHO Surveyor Power

Produce an authoritative map that another role can act on without rediscovering the environment.

## Required composition

Load `$echo-proofline-verification`, `$echo-risk-action-review`, `$echo-runbook-generation`, and `$superpowers:systematic-debugging`.

## Survey loop

1. Define the survey boundary, decision it supports, freshness target, and prohibited data.
2. Resolve live nodes, repositories, services, processes, ports, storage, databases, queues, dependencies, and owners through authoritative sources.
3. Cross-check declared inventory against runtime state, git, service managers, network bindings, and data stores.
4. Model relationships and critical paths. Label confirmed facts, inferred edges, unreachable targets, stale declarations, and unknown ownership.
5. Rank drift and gaps by blast radius, recoverability, security, cost, and impact on active missions.
6. Validate representative paths end to end and produce remediation-ready findings with exact evidence and commands.
7. Publish a dated manifest or map, register it, persist material topology decisions, and define the refresh path.

## Capability contract

Use `echo.monitor.*`, `echo.node.*`, `echo.fs.*`, read-only `echo.psql.*`, `echo.logs.*`, `echo.logaggregator.*`, `echo.git.*`, and bounded `echo.shell.*` through the scoped broker. Resolve moving addresses and identifiers live.

## Proof gate

Inventory counts are not a system map. Completion requires source provenance, freshness timestamps, relationship validation, drift classification, and actionable ownership for critical gaps.
