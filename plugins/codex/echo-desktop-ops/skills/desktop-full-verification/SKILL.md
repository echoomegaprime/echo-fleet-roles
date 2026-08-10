---
name: desktop-full-verification
description: Inspect, test, package, certify, and report Echo Desktop readiness through the bounded Echo Desktop Ops MCP, including source, Fleet, provider, runtime, installer, evidence, and release-gate verification.
---

# Echo Desktop Full Verification

Use this skill to inspect, test, package, certify, or report readiness for Echo Desktop.

## Required workflow

1. Call desktop_environment_status and desktop_project_snapshot.
2. Call desktop_cli_status, desktop_fleet_status, desktop_shared_state, desktop_provider_status, desktop_mcp_status, and desktop_runtime_status.
3. Treat a dirty worktree, missing installer, failed mandatory check, missing evidence, or unresolved high-severity incident as a release blocker.
4. During development, call desktop_run_verification with profile full.
5. For release certification, call desktop_run_verification with profile release.
6. Call desktop_release_decision using the returned report ID.
7. Report the current branch and commit, uncommitted work, major implemented systems, CLI and Fleet state, test results, dependency audit, installer status, blocking checks, and exact readiness verdict.

## Rules

- Never expose credentials, environment values, tokens, or private customer data.
- Never use phase labels or progress percentages as proof of readiness.
- Use desktop_read_project_file and desktop_search_project for source inspection.
- A final setup executable and release-profile evidence are mandatory for promotion.
