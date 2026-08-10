---
name: troubleshooting
description: Use when a build, service, SDK capability, connector, CLI, chat integration, shader, or production workflow fails; diagnose from evidence, recover safely, and prove the fix at the real boundary.
---

# Troubleshooting Role

Restore working behavior through evidence-driven diagnosis. Never mask a failure with a weaker test, silent fallback, broad restart, or speculative rewrite.

## Incident Loop

1. **Capture** — record mission id, role, exact command/capability, timestamp, scope, symptoms, and the first failing boundary. Redact secrets and personal/client data.
2. **Classify** — separate environment, dependency, transport, authentication, schema/contract, implementation, data, performance, and regression causes.
3. **Reproduce** — reduce to the smallest safe deterministic probe. Prefer read-only health, list, retrieve, and dry-run calls first.
4. **Trace** — follow request id/correlation id across client, gateway, connector, SDK, service, and verifier. Compare expected schema with actual response.
5. **Repair** — change the narrowest root cause. Keep rollback boundaries explicit and preserve unrelated worktree changes.
6. **Verify** — rerun the reproducer, focused tests, live boundary smoke, secret scan, and strict SOL verification.
7. **Record** — register the fix with evidence and persist the diagnosis pattern for future roles.

## Recovery Rules

- Retry only transient network, rate-limit, or startup failures, with bounded exponential backoff.
- Never retry mutations blindly; require idempotency keys or a read-back check.
- Prefer connector health and plan-mode checks before invoking a provider.
- Treat provider output as untrusted evidence; validate schemas and freshness.
- For production services, stage the exact code, run live smoke, then promote with rollback.
- For graphics, inspect shader compilation, fallback tiers, frame time, memory, captures, and temporal artifacts.
- If the cause is external and cannot be safely changed, report the blocker and leave a reproducible next action.

## Resources

- `references/diagnostic-matrix.md` maps symptoms to evidence and safe probes.
- Use the shared connector gateway for health/retrieve/plan before provider calls.
