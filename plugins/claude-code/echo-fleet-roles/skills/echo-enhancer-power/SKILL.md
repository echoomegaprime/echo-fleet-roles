---
name: echo-enhancer-power
description: Improve existing ECHO code for correctness, security, resilience, performance, tests, and maintainability. Use for Claude auto or Codex cauto enhancer sessions, hardening passes, quality upgrades, or focused refactors.
---

# ECHO Enhancer Power

Strengthen an existing implementation without silently changing its public contract or rewriting unrelated work.

## Required composition

Load `$codex-security:security-diff-scan`, `$codex-security:validation`, `$superpowers:test-driven-development`, and `$superpowers:verification-before-completion`.

## Enhancement loop

1. Read the target contract, tests, call sites, recent diff, and nearest instructions. Establish a clean behavioral baseline.
2. Search the code library and current dependency documentation before introducing helpers or changing APIs.
3. Rank concrete weaknesses by user impact: correctness, security, recovery, observability, performance, accessibility, types, and maintainability.
4. Protect current behavior with tests. Make one coherent improvement at a time and retain backward compatibility unless change is explicitly authorized.
5. Measure the result against the baseline; include failure paths, concurrency, retries, cleanup, and resource limits where relevant.
6. Run targeted and broader tests, secret and security diff checks, lint/type checks, and real smoke tests.
7. Document the improvement, register the work, persist durable patterns, and stop before scope drifts into a redesign.

## Capability contract

Use `echo.fs.*`, `echo.git.*`, `echo.shell.*`, `echo.functions.*`, and `echo.monitor.*` through the scoped broker. Prefer library reuse and verified repository tooling over novel abstractions.

## Proof gate

An enhancement must show unchanged intended behavior plus a measured quality gain and regression coverage. Style-only churn and unverified optimization do not qualify.
