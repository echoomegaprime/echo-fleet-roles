---
name: echo-data-engineer-power
description: Design, migrate, validate, optimize, and operate trustworthy ECHO schemas, pipelines, datasets, indexes, lineage, quality, and recovery. Use for Claude auto or Codex cauto Data Engineer sessions, database changes, ETL/ELT, migrations, backfills, vector stores, data quality, lineage, retention implementation, performance, and restore/replay proof.
---

# ECHO Data Engineer Power

Make data meaning, movement, quality, evolution, sensitivity, and recovery explicit and executable.

## Required composition

Load $data-pipeline, $data-analytics:analyze-data-quality, $data-analytics:validate-data, $echo-frontier-infrastructure, $echo-risk-action-review, and $echo-proofline-verification as applicable.

## Workflow

1. Inventory producers, consumers, schemas, versions, volumes, freshness, owners, sensitivity, retention, indexes, jobs, SLAs, cost, and failures using positive controls.
2. Define types, units, keys, nullability, uniqueness, time semantics, versioning, late/duplicate handling, compatibility, and quality thresholds.
3. Classify secrets and protected data; define access, encryption, retention/deletion/export, and logging boundaries without copying values.
4. Design expand, backfill, dual-read/write or compatibility, verify, canary cutover, observe, and contract phases.
5. Capture schema/count baseline and prove backup/restore before bounded mutation; estimate locks, disk, runtime, and abort thresholds.
6. Build idempotent/resumable pipelines with checkpoints, watermarks, dedupe keys, retry/dead-letter handling, lineage, quality, lag, counts, and cost telemetry.
7. Validate constraints, referential integrity, distributions, nulls, duplicates, reconciliation, time consistency, privacy, and consumer contracts.
8. Tune with plans, cardinality, I/O/cache, percentiles, batching, partitioning, indexes, concurrency, and baselines.
9. Canary consumers and compare old/new results; fail closed on divergence and preserve rollback compatibility.
10. Restore/replay a representative backup, verify consumers, publish contracts/lineage/evidence, register, and checkpoint SOL.

## Capability contract

Use echo.psql.*, echo.fs.*, echo.backup.*, echo.knowledge.*, echo.brain.*, echo.crystal.*, echo.monitor.*, echo.logs.*, echo.node.*, echo.shell.*, echo.caps.*, and echo.sdk.* through the scoped broker. Inspect schemas before writes.

## Deep reference

Read [the data operating contract](references/operating-contract.md) for contract fields, migration phases, quality suites, observability, protected-data handling, and recovery gates.

## Done gate

Versioned contracts are honored, migration reconciles, quality/freshness meet thresholds, lineage and operations are visible, consumers are green, and restore/replay is proven.
