---
name: echo-cli-build-power
description: Drive durable autonomous builds through ECHO CLI lanes with ownership, resumability, tests, and truthful completion. Use for Claude auto or Codex cauto cli-build sessions or long-running command-line build missions.
---

# ECHO CLI Build Power

Turn a build specification into a resumable, observable, collision-safe CLI mission that survives routine failures and ends in verified artifacts.

## Required composition

Load `$echo-codex-coordinator`, `$superpowers:test-driven-development`, `$superpowers:verification-before-completion`, and `$echo-risk-action-review`.

## CLI build loop

1. Retrieve the full queue item or mission, repository state, lane availability, prior checkpoints, and ownership records.
2. Define exact owned paths, phase acceptance tests, resume state, time and resource limits, halt control, and rollback.
3. Use the best live lane for the task; prefer short low-latency lanes for small loops and durable full lanes for multi-file objectives.
4. Execute one acceptance-gated slice at a time. Checkpoint after material progress and recover transient auth, process, or dependency failures independently.
5. Run tests in the real required environment, capture logs and artifacts, and reject honor-system progress.
6. Commit queue-owned work with the required identity, update queue state only from evidence, and release ownership cleanly.
7. Register direct builds, persist decisions, close SOL only after strict verification, then claim the next eligible objective.

## Capability contract

Use `echo.lanes.*`, `echo.fs.*`, `echo.git.*`, `echo.shell.*`, `echo.logs.*`, `echo.logaggregator.*`, and base queue/build capabilities through the scoped broker. Discover a service-specific control capability before falling back to bounded shell control.

## Proof gate

Completion requires committed or registered artifacts, passing acceptance tests, reproducible commands, correct lane and build identity, and no leaked ownership or stale running status.
