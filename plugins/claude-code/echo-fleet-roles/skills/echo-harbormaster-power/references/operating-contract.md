# Harbormaster release operating contract

## Release packet

Require candidate commit/digest, Judge manifest, dependencies and configuration revision, target environment, topology, staging endpoint, SLO/budget thresholds, critical journeys, migration versions, feature flags, rollback artifact/config/schema compatibility, backup/restore evidence, communications, and owners.

## Baseline capture

Record version identity, process/service health, request volume, error and timeout rate, latency percentiles, saturation, queues, worker lag, dependency health, data-quality indicators, storage headroom, current schema, and business-event baseline. Use the same measurement definitions for canary comparison.

## Staging gate

- exact artifact identity matches Judge manifest;
- production-shaped environment, dependencies, secrets references, and routing;
- real HTTP/API/user journeys with empty, missing, malformed, unauthorized, and degraded inputs;
- migrations on representative data with timing, locks, disk, rollback, and reconciliation;
- background jobs, webhooks, schedules, emails, files, caching, observability, headers, SEO/accessibility essentials where applicable;
- no new critical/high findings or unresolved candidate mismatch.

## Migration sequence

Expand schema and indexes compatibly. Backfill in bounded resumable batches with checkpoints. Dual-read/write or compatibility views when needed. Reconcile old/new results. Cut over a canary. Observe. Contract only after rollback window, retention rule, and all consumers are proven migrated.

Every step needs idempotency, pre/post counts, lock/runtime estimate, abort threshold, backup, and reversal or forward-recovery path.

## Canary thresholds

Declare before launch: error/timeout delta, latency percentile delta, saturation, crash/restart rate, queue lag, data divergence, business conversion/task success, and observation duration. A missing signal blocks progression. Never redefine thresholds after seeing results.

## Rollback triggers

Wrong artifact/config, failed critical journey, auth/data boundary defect, schema incompatibility, error/latency/saturation threshold, data divergence, observability loss, or unexplained downstream failure. Halt traffic progression, preserve logs/traces, restore last-known-good artifact/config, execute compatible data recovery, and verify user journeys plus baseline recovery.

## Release manifest

Include release ID, candidate and production identities, Judge manifest hash, staging/canary/production timestamps, commands/automation version, migration versions/results, thresholds and observations, rollback target/status, redacted evidence hashes, incidents, exceptions, residual risk, monitor handoff, and registration IDs.

## Failure routing

Code/config logic defect returns to Builder/Enhancer. Security to Sentinel. Data contract/migration to Data Engineer. Experience/accessibility to Experience Designer. Instrument or unexplained runtime discrepancy to Troubleshooter. Harbormaster never hot-patches around the gate.
