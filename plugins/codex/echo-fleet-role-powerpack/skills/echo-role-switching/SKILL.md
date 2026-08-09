---
name: echo-role-switching
description: Select and switch among the 30 ECHO fleet roles inside one active Codex build. Use when an objective changes operating domains or needs a different role's focused workflow. Do not use to bypass host permissions, authorization, or required verification.
---

# ECHO Role Switching

Use the role runtime as an explicit specialization boundary, not as a permission escalation mechanism.

## Workflow

1. Inspect the current role with `echo-role --json current` and the available roles with `echo-role --json list`.
2. Pick the narrowest role whose primary skill matches the next material phase of the objective.
3. Switch atomically with `echo-role --json switch <role> --expected-current <current> --idempotency-key <stable-key> --reason "<phase>"`.
4. Read and follow the returned `primary_skill`. Load composed skills only when their domains apply.
5. Continue in the same terminal and session. The plugin hook reinforces the selected role on later prompts.
6. Record the transition in delivery evidence when it materially changed architecture, security, release, or operational responsibility.

## Selection rules

- Stay in the current role when it already covers the next work.
- Switch for a real domain boundary: design to build, build to verification, security testing to remediation, or release to certification.
- Never use role switching to claim tools, scopes, credentials, or authority the host did not expose.
- Preserve separation of duties: the builder must not self-issue an independent certification.
- On a state conflict, reread `current`, reassess the live phase, and retry with a new expected-current value.

## Output

Report the old role, new role, reason, primary skill, and whether the transition changed state. A new Codex session is needed once after first installing or enabling the plugin; subsequent role changes do not require a reboot or another terminal.
