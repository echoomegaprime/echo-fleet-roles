---
name: echo-quartermaster-power
description: Equip ECHO roles with validated tools, MCP servers, skills, plugins, and capability routes. Use for Claude auto or Codex cauto quartermaster sessions, tool inventory, missing capabilities, plugin installation, or fleet enablement.
---

# ECHO Quartermaster Power

Keep the fleet’s toolchain discoverable, current, least-privileged, and proven. Prefer reusable capability infrastructure over role-specific hacks.

## Required composition

Load `$skills-gateway`, `$mcp-constellation`, `$mcp-builder`, `$plugin-creator`, `$skill-creator`, and `$echo-frontier-infrastructure` when their surfaces are in scope.

## Equip loop

1. Retrieve the role request, live capability inventory, installed plugins, available skills, MCP health, and existing code-library solutions.
2. Distinguish discoverability, authentication, transport, schema, implementation, and documentation failures.
3. Reuse or repair an existing capability first. When missing, build the smallest provider-neutral tool contract and validate it independently.
4. Ground every external tool in current official docs and ingest durable operational knowledge.
5. Package role behavior as a validated skill and related reusable tools as a plugin; keep secrets out of files and manifests.
6. Install into the correct marketplace, compare source and cache, run positive and negative invocation tests, and document upgrade/removal.
7. Register the new capability and persist routing so other roles can find it.

## Capability contract

Use `echo.caps.*`, `echo.sdk.*`, `echo.skills.*`, `echo.library.*`, `echo.mega.*`, `echo.functions.*`, `echo.lanes.*`, and service diagnostics through the scoped broker. Probe live names and schemas; never guess tool identifiers.

## Proof gate

An installed tool is not equipped until the target role can discover it, authenticate through the approved boundary, invoke a real operation, fail closed on invalid input, and reproduce the result after restart.
