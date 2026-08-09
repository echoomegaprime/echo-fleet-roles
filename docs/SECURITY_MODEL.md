# Security Model

## Trust boundaries

- User instruction to host agent.
- Host agent to role runtime.
- Role runtime to local SQLite state.
- Host lifecycle system to plugin hook.
- Host agent to any external SDK, MCP server, shell, browser, or security platform.
- Builder output to independent certification and release control.

## Controls

- Strict registry parsing rejects unknown fields, missing arrays, bad aliases, and role-count drift.
- SQLite transactions, WAL, idempotency keys, and expected-current fencing protect transition integrity.
- Hooks only read registry and state; all exceptions fail open so role context cannot prevent host startup.
- No secrets, tokens, commands, prompts, or tool output are stored in role state.
- Roles declare intended capability families but cannot create a tool, credential, permission, or authorization.
- Security and reverse-engineering skills require authorized scope and preserve evidence, cleanup, and stop conditions.
- Builder and independent certification duties remain separated.
- Public plugin validation scans for private network and infrastructure literals.

## Threats considered

Prompt injection cannot change the registry or host authorization. Path traversal is avoided by resolving packaged paths from fixed roots. SQL injection is avoided through parameterized SQLite statements. Transition replay is bounded by unique idempotency keys. Concurrent overwrite is detected with expected-current fencing. Malicious registry additions fail strict validation. Hook denial of service is reduced through read-only access, short SQLite timeouts, bounded context, and fail-open exception handling.
