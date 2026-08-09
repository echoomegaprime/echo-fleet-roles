---
name: echo-role-switching
description: Select and switch among the 30 ECHO fleet roles inside one active Claude Code build. Use when an objective changes operating domains or needs a different role's focused workflow. Do not use to bypass host permissions, authorization, or required verification.
---

# ECHO Role Switching

Use `echo-role` to inspect, atomically switch, and audit role specialization without opening another terminal. Choose the narrowest matching role, use `--expected-current` and a stable `--idempotency-key`, then load the returned primary skill. Stay within the host's real authorization and tool surface, preserve separation of duties, and record material transitions in delivery evidence. First installation may require one new Claude Code session to load the plugin; subsequent changes are same-session.
