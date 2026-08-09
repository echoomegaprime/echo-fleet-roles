# Data Engineer operating contract

## Inventory fields

Producer/owner, consumer/owner, dataset/table/topic/index, schema/version, keys, volume/growth, throughput, freshness/lag, retention, sensitivity, residency, access, encryption, storage, partitions/indexes, jobs/schedules, dependencies, SLA/SLO, cost, backup, restore RTO/RPO, and active incidents.

## Data contract

Define names and business meaning, types/precision/units, required/null/default, primary/natural/idempotency keys, uniqueness and references, event and processing timestamps/timezone, ordering, update/delete semantics, late/duplicate policy, schema compatibility, quality thresholds, owner, change process, and deprecation window.

## Migration plan

1. Baseline schema, counts, distributions, consumers, query plans, storage, and performance.
2. Verify backup and representative restore.
3. Expand compatibly with idempotent DDL and bounded lock/runtime.
4. Deploy compatible writers/readers.
5. Backfill in resumable batches with checkpoint, throttle, reject capture, and reconciliation.
6. Dual-read/write or compare old/new where risk warrants.
7. Canary cutover and monitor divergence, lag, errors, resource and business signals.
8. Complete cutover, preserve rollback window, then contract after all consumers and retention rules permit.

Every phase has precondition, command/version, expected observation, abort threshold, evidence, rollback/forward-recovery, and owner.

## Quality suite

Schema and type conformity; key uniqueness; required/null; domain/range; referential integrity; duplicate and idempotency behavior; distribution/drift; temporal order/freshness; completeness; cross-source reconciliation; sampled semantic correctness; privacy/access boundaries; consumer contract; and old/new comparison.

Quality thresholds are explicit and segmented. Quarantined/rejected records remain countable, inspectable through protected paths, and replayable.

## Pipeline reliability

Use immutable raw inputs where feasible, checkpoints/watermarks, idempotency keys, bounded retry/backoff, dead-letter/quarantine, backpressure, atomic or transactional boundaries, schema registry/versioning, deterministic transformations, lineage, replay tooling, and resource/cost limits.

## Observability

Emit input/output/reject/duplicate counts, freshness and lag, checkpoint/watermark, duration/throughput, retry/dead-letter, data-quality results, schema version, lineage/run ID, resource/cost, and consumer health. Alert on sustained breaches with runbook links.

## Protected data

Minimize collection and copies; use scoped access and encryption; redact logs/samples; use synthetic or masked test data; enforce retention/deletion/export; record lawful/product purpose from Compliance Officer; and keep client/identity/bank/tax records out of prompts and reports.

## Recovery proof

Restore into isolated storage, verify schema and hashes/counts, replay from checkpoint, reconcile to a declared point, reconnect a representative consumer, measure RTO/RPO, document gaps, and preserve the recovery artifact metadata. A backup without restore is unproven.
