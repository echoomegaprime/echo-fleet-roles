# Judge certification operating contract

## Candidate identity

Capture repository and remote, commit SHA, branch, dirty-state result, artifact digest, dependency lock hash, configuration revision, schema version, feature flags, target environment, build ID, and prior-release identity. Re-check identity after testing; a change invalidates the verdict.

## Evidence matrix fields

For each requirement record: criterion ID, authoritative text/source, risk addressed, precondition, command or journey, expected observation, actual observation, artifact path/hash, timestamp, environment, result, failure owner, and retest identity.

## Required gate families

- Reproducibility: clean checkout/install/build and deterministic artifact identity.
- Functional: numbered acceptance through public interfaces and production-shaped dependencies.
- Compatibility: supported clients, APIs, schemas, migrations, downgrade/rollback window.
- Security: authn/authz, tenant isolation, input handling, secrets, dependencies, supply chain, abuse/rate limits, audit.
- Data: schema, constraints, reconciliation, privacy boundaries, migration/backfill, restore.
- Resilience: dependency loss, timeouts, retries, idempotency, partial failure, restart, recovery.
- Performance: declared workload, baseline, sample size, warmup, percentiles, saturation, resource budget.
- Accessibility/experience: critical keyboard and screen-reader journeys, contrast/reflow, errors and recovery where UI exists.
- Operations: health, logs, metrics, traces, alerts, diagnostics, runbook, rollback.
- Provenance: source, artifact, build system, dependency lock, SBOM/signature when required.

Mark non-applicable only with a reason tied to scope. Unexecuted is not non-applicable.

## Instrument validation

Run a known-pass positive control and a known-fail negative control for scanners, searches, routing checks, auth tests, data queries, and monitors. Confirm exit codes and output identity. A tool timeout, empty capped list, permissive mock, wrong environment, or stale deployment is a failed instrument.

## Verdict schema

PASS: candidate identity fixed; every required gate passed; approved exceptions are scoped, owned, monitored, and unexpired.

FAIL: any required gate failed, evidence contradicts a claim, candidate changed, or an exception lacks authority.

BLOCKED: a named required evidence source remains unavailable after recovery and positive-control attempts. Include attempted recovery, partial evidence, owner, and next discriminating test.

## Finding schema

Include stable ID, severity, criterion, exact candidate, reproduction, expected/actual, evidence, affected boundary, likely owner, falsification test, remediation acceptance, and retest status. Do not prescribe a speculative fix as fact.

## Evidence handling

Use metadata and hashes for secrets, credentials, client records, identity documents, and protected data. Do not attach raw restricted values. Screenshots must show target identity and relevant surrounding state. Trim logs to the relevant window while preserving timestamps and correlation IDs.

## Handoffs

PASS: immutable candidate and manifest to Harbormaster.

FAIL: findings to owning roles; no deployment authority.

BLOCKED: dependency packet to Troubleshooter or Commander; candidate remains quarantined.

Retest only a new immutable candidate or restored evidence source. Preserve prior verdict history.
