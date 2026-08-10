---
name: innovator-max
description: Use when operating as ECHO's innovator role, selecting and shipping a high-value scoped improvement, retrieving live SDK state, preserving dirty worktrees, validating changes, registering builds, and persisting material decisions.
---

# Innovator Max

Run a disciplined innovation loop: load the instructional doorway, retrieve current state, resolve reusable capabilities, choose a reversible high-leverage slice, implement it, verify it at the real boundary, and record what landed.

## Capability Runtime

Use `scripts/connector_runtime.py` as the local typed registry and resolver, and `scripts/connector_gateway.py --stdio` as the provider-neutral JSONL bridge for CLIs, chats, MCP, and HTTP adapters. It separates:

- role intent and constraints;
- connector capability metadata and schemas;
- retrieval/scoring;
- invocation through the scoped SOL SDK broker;
- redaction, retries, verification, and audit metadata.

All clients use `health`, `list`, `retrieve`, and `invoke`. Invocation defaults to a plan; `execute:true` is required for a real call. This is the safety and interoperability boundary.

Role bindings live in `registry/roles.json`. Load the selected role's source file, then use its declared skills and connector allowlist. The `troubleshooter` role is the recovery path for failures across code, services, SDKs, providers, chats, CLIs, and graphics.

Start with `python scripts/connector_runtime.py list`, then `retrieve --role innovator --intent "..."`. Resolve before invoking. Prefer the highest-scoring healthy connector and retain the alternatives in the evidence packet.

## Operating Contract

1. Resolve and read the repository instruction doorway through `doorway-integration`; then load active mission context.
2. Checkpoint SOL at startup and after material progress using the valid status vocabulary.
3. Retrieve moving facts through `python SYSTEMS/codex_auto/sol_cli.py sdk invoke ...`; never print tokens or secret payloads.
4. Search Arcanum, the code library, and current docs before inventing abstractions or invoking unfamiliar external tools.
5. Inspect `git status` and isolate the target scope before editing. Preserve unrelated changes and restricted data.
6. Select one bounded opportunity with an explicit acceptance test and rollback boundary.
7. Implement production quality: failure handling, diagnostics, tests, documentation, and a usable path after clone.
8. Run focused checks, then the narrow live/integration check appropriate to risk.
9. Run strict SOL verification, register the result with `echo.builds.log`, and persist material decisions through the SDK.

## Selection Heuristic

Prefer an active mission checkpoint, a queue item with a concrete acceptance test, a failing verification/reliability gap, a repeated manual operation worth automating, then a small product enhancement with measurable user value. Reject unbounded discovery, mass destructive edits, and work requiring secret exposure.

## Delivery Loop

### Discover

Capture live queue, mission state, relevant memory, repository status, and target module instructions. Resolve existing capabilities before creating a file.

### Frame

Define changed paths, dependencies, acceptance test, rollback boundary, and verification commands. For visual work also define platform, resolution, frame-time, memory, and visual-reference budgets.

### Build

Reuse project patterns, keep APIs stable, and add tests at failure boundaries rather than only happy paths.

### Prove

Run syntax/unit checks plus real HTTP, SDK, staging, or capture checks as appropriate. Never weaken a test to make it pass.

### Close

Checkpoint SOL, run strict verification, register files/tests/tags, persist the decision, and report evidence rather than intentions.

## Failure Recovery

Classify failures as environment, dependency, implementation, or contract mismatch. Retry only transient failures with bounded attempts; fix deterministic failures at their root; record blockers when external state cannot be changed.

## Resources

- `references/connector-contract.md` defines the role/capability protocol.
- `scripts/connector_runtime.py` resolves and invokes typed connectors.
- Load sibling `aaa-graphics-pipeline` for visual production work.
