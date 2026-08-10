---
name: echo-reverse-engineering
description: Perform authorized, evidence-preserving reverse engineering and clean-room reconstruction of websites, web apps, mobile apps, desktop programs, binaries, firmware, APIs, and protocols. Use for requests to inspect, scrape, map, disassemble, decompile, behaviorally specify, reproduce, migrate, or build an upgraded ECHO-compatible replacement from an ECHO-owned, user-provided, public-interface, donated-lab, or explicitly authorized target.
---

# ECHO Reverse Engineering

Turn an authorized target into a verified behavioral specification and a clean-room ECHO replacement. Preserve evidence, route dangerous artifacts to isolated lab nodes, and prove both parity and improvement.

## Non-negotiable boundary

- Fully analyze ECHO-owned, user-provided, donated-lab, or explicitly authorized targets within the granted scope.
- For an unaffiliated third-party public website, observe only public behavior and public responses. Recreate behavior clean-room without copying proprietary source, protected media, private data, credentials, or trademarks.
- Do not defeat licensing, DRM, authentication, access controls, or anti-abuse systems outside explicit authorization. Never reuse discovered secrets; redact evidence and remediate ECHO-owned exposures.
- Treat unknown binaries and firmware as hostile. Analyze or execute them only in an isolated Crucible or ANVIL lab environment, never on HAMMER or production FORGE.

## Workflow

### 1. Open an evidence-preserving case

Create `RE_CASE.md` and `EVIDENCE_MANIFEST.json`. Record authorization class, target, scope, exclusions, provenance, acquisition time, hashes, tools, versions, and evidence paths. Read the applicable instruction chain, then search Arcanum, Knowledge Forge, and the Code Library before designing anything new.

### 2. Select the analysis lane

Read [tool-routing.md](references/tool-routing.md), discover the live capability contract, and select the smallest sufficient surface:

- Web systems: ShadowGlass for DOM, accessibility tree, JavaScript state, console, network, response bodies, HAR, storage-visible behavior, responsive states, and performance.
- Native binaries: Ghidra-backed function, import, string, and focused decompilation capabilities; add capa, FLOSS, YARA, or debugger/emulator lanes only when the live inventory supports them.
- Mobile apps: APK decompilation, secret and endpoint scanning, manifest/resource mapping, plus an isolated device or emulator for authorized runtime behavior.
- Firmware: immutable acquisition, hashes, partition and filesystem mapping, SBOM, update/signature analysis, and isolated emulation where possible.
- APIs and protocols: capture only traffic the authorization permits; derive schemas, state transitions, error behavior, rate limits, idempotency, and compatibility constraints.
- Source-available programs: map build graph, runtime topology, persistence, dependencies, configuration, and public contracts before changing code.

### 3. Build the behavioral specification

Document:

- Features, routes, commands, states, workflows, and edge cases.
- UI state machine, responsive behavior, accessibility semantics, and visual tokens.
- Data model, APIs, authentication, authorization, tenant boundaries, errors, and recovery.
- Dependencies, SBOM, trust boundaries, attack surface, privacy behavior, and observability.
- Performance, reliability, and resource baselines under reproducible workloads.
- A parity matrix linking each observed behavior to evidence and an acceptance test.

Label every statement `observed`, `inferred`, or `unknown`. Resolve important unknowns with discriminating tests; do not present decompiler output or guesses as ground truth.

### 4. Reconstruct and upgrade

Create a private ECHO repository before implementation. Write a phased specification with executable acceptance tests. Implement from the behavioral specification and public contracts, not copied proprietary code.

Apply upgrades across:

- Security: least privilege, tenant isolation, input validation, safe secret handling, secure defaults, dependency controls, and audit trails.
- Reliability: migrations, backups, rollback, timeouts, retries, idempotency, graceful degradation, and failure injection.
- Performance: measured query, cache, concurrency, startup, memory, bandwidth, and latency improvements.
- Product and UX: accessible responsive flows, coherent design, useful diagnostics, and features grounded in verified gaps.
- Operations: structured telemetry, health/readiness checks, reproducible builds, staging gates, and documented recovery.

### 5. Prove parity and superiority

- Run black-box comparison tests using identical permitted fixtures and record intentional divergences.
- Run unit, integration, regression, security, and end-to-end suites against real dependencies where required.
- Compare performance with the same workload and environment; report distributions and resource usage, not a single best run.
- Stage the exact release candidate, run live smoke tests, validate rollback/recovery, and independently verify evidence.
- Fail closed on missing provenance, untested critical paths, secret exposure, tenant-boundary ambiguity, or unexplained parity gaps.

### 6. Close the case

Deliver `RE_CASE.md`, `EVIDENCE_MANIFEST.json`, `BEHAVIORAL_SPEC.md`, `PARITY_MATRIX.md`, `THREAT_MODEL.md`, `UPGRADE_BACKLOG.md`, and `ACCEPTANCE_REPORT.md`. Register the build, persist material decisions, and report exact tests, hashes, deployment state, and remaining hard limits.

## Failure rules

- A successful decompile is not a behavioral specification.
- HTTP 200 is not proof of page identity, content, or correct state.
- Empty tool output requires a positive control before it can be treated as a real negative.
- Publicly reachable assets are not automatically licensed for reuse.
- "Feature complete" is false until parity, security, and live acceptance evidence passes.
- If a required capability is missing or broken, repair or register the governed path; do not silently weaken the method.
