# Product Manager operating contract

## Problem brief

Record target user/segment, job, trigger, desired progress, current path/workaround, pain frequency/severity, observed evidence, affected cohort size, business/mission impact, why now, constraints, unknowns, and explicit non-goals. Separate facts, interpretations, and assumptions.

## Evidence sources

Use interviews and observation, beta feedback, support/incident themes, product analytics, funnel/cohort behavior, retention/churn, task success/time, sales/marketing evidence, cost-to-serve, competitive/current official sources, and system operations. Synthetic users and internal opinions are hypotheses, not demand proof.

## Metric tree

Define outcome metric, formula, unit, source/table/event, filters, cohort, baseline window, comparison window, owner, cadence, data-quality checks, minimum meaningful change, and guardrails. Leading indicators must causally support the outcome; vanity totals do not substitute.

## Experiment card

Include uncertainty, hypothesis, target segment, intervention, control/comparison, primary and guardrail metrics, sample/exposure, duration, success threshold, stop threshold, instrumentation validation, cost, privacy/compliance, and decision for each result. End experiments with a decision.

## Prioritization record

Score value, reach, confidence/evidence strength, effort, time-to-learning, strategic fit, dependency readiness, operational burden, risk reduction, reversibility, and opportunity cost. Preserve inputs and rationale; do not hide a Commander priority behind a fake score.

## Product contract

Include context, users, problem, outcome/metrics, scope, non-goals, functional requirements, nonfunctional budgets, journey, states/errors, data contracts, privacy/compliance, accessibility, instrumentation, dependencies, risks, numbered acceptance, phased rollout, support/operations, kill/rollback criteria, and owners.

Requirements state observable behavior and constraints. Architecture decisions belong to Architect unless a specific implementation is itself a product requirement.

## Handoffs

- Experience Designer: journeys, comprehension, interaction, accessibility.
- Architect: boundaries, ADRs, dependencies, technical risk.
- Data Engineer: events, schemas, quality, migration, metrics.
- Compliance Officer: obligations, consent, claims, retention.
- Builder/Enhancer: implementation and production quality.
- Judge: release acceptance and evidence matrix.
- Harbormaster: rollout, thresholds, rollback.
- Marketing/Beta: acquisition and real-user learning.

## Outcome review

After release validate instrumentation, compare cohorts with baseline, inspect guardrails, segment effects, qualitative feedback, incidents, support burden, revenue/cost, and unintended behavior. Decide expand, iterate, hold, or retire with evidence and update the roadmap and acceptance system.
