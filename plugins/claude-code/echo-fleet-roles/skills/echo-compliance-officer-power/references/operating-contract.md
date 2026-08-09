# Compliance Officer operating contract

## Scope record

Record product/version/release, legal entity, jurisdictions, user categories/ages, data categories, processing purposes, channels, vendors/subprocessors, payment/communications/advertising, accessibility context, public claims, licenses, contracts, retention, automated/AI decisions, and assessment date.

## Source discipline

Prefer controlling statutes/regulations, regulator guidance, standards bodies, signed contracts, licenses, and official vendor terms. Record title, authority, jurisdiction, section, URL/doc identity, effective date, retrieval date, applicability trigger, and interpretation uncertainty. Re-check temporally unstable authority before a release decision.

## Obligation register fields

Stable ID, domain, requirement/citation, classification (mandatory/contract/policy/recommended), applicability and trigger, product/data/process scope, control objective, implementation, owner, evidence, positive/negative test, cadence, retention, severity, remediation, exception, expiry, and last/next review.

## Control domains

- privacy notice, minimization, purpose, consent/basis, preferences, access/export/correction/deletion;
- retention, legal hold, deletion verification, backup propagation;
- identity, least privilege, tenant separation, logging, encryption, incident/breach readiness;
- accessibility and accommodation across critical journeys;
- marketing/communications consent, sender identity, opt-out, rate/platform rules;
- claims, pricing, disclosures, endorsements, substantiation, dark-pattern avoidance;
- software/content/data/model licenses and attribution;
- vendor/subprocessor due diligence, contracts, data flow, changes, termination/export;
- financial, tax, title, health, family/personal-data product boundaries as applicable;
- AI training use, transparency, evaluation, human review, provenance, retention, and incident controls.

## Control test

Tie objective to actual code/config/UI/runtime and a repeatable positive and negative test. Verify identity and environment. Record expected/actual, evidence hash/path, date, reviewer, result, limitations, and recurrence signal. A policy or vendor checkbox alone does not prove downstream behavior.

## Finding severity

Consider mandatory nature, affected people/data, exploitability/exposure, scope, duration, detectability, reversibility, contractual consequence, and evidence confidence. Record owner, due date, compensating control, acceptance test, residual risk, and release effect.

## Exceptions

Require named authority, obligation/control, exact scope, evidence/rationale, compensating control, risk owner, monitoring, start/expiry, and review. Expired or scope-mismatched exceptions fail closed.

## Release posture

COMPLIANT: mandatory controls for exact scope are implemented and evidenced; exceptions valid.

NONCOMPLIANT: a mandatory control fails, evidence contradicts claims, or exception is invalid.

BLOCKED: controlling authority or mandatory evidence is unavailable after documented retrieval/recovery. Unknown is not compliant.

## Protected evidence

Keep personal/client/tax/identity/bank/credential values in authorized systems. Reports use redacted metadata, counts, paths, control IDs, timestamps, and hashes. Apply least access and do not create extra evidence copies. Public claims link to product proof, not confidential records.
