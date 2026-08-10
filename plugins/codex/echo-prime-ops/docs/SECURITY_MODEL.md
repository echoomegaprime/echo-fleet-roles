# Security and threat model

## Trust boundaries

The design treats these as separate boundaries: user to ChatGPT; ChatGPT to the public MCP edge; edge to the
MCP service; MCP service to Echo Auth, SDK registry, Persona Forge, and official public-safety adapters; plugin
bundle to the local Codex host; and skill instructions to tools. There is no widget boundary because v1 has no
custom UI.

## Threats and implemented mitigations

| Threat | Mitigation |
|---|---|
| Prompt or indirect prompt injection | Loaded skill treats repository, registry, provider, context_tools, logs, and tool output as untrusted data; tools are narrow and read-only; no generic invoke surface |
| Cross-tenant access, IDOR, function-level authorization | Server-side subject allowlist, tenant/role binding, exact per-tool scopes, no model-selected tenant |
| Excessive scopes | Four minimal read scopes, declared per tool; no write/admin scope |
| Token substitution, audience confusion | Exact resource binding at authorize, token, and every tool call |
| Replay | High-entropy one-time codes, PKCE S256, bounded state, expiration, atomic consumption |
| Credential or log leakage | Key-name and text redaction; body size caps; no password/token trace; safe errors |
| SSRF and DNS rebinding | Fixed allowlisted upstream base URLs from server configuration; no caller-supplied URL |
| Path traversal and command injection | No file/path or command tool; strict identifiers; no shell interpolation |
| SQL/NoSQL injection and mass assignment | No client-supplied query language; strict schemas and allowlisted fields |
| XSS, unsafe Markdown, postMessage, open redirects | No custom UI; exact registered redirect URI; login page escapes values and uses nonce CSP |
| Resource exhaustion and unbounded pagination | Request body limits, string/array/numeric bounds, final-result caps, bounded retry and timeout |
| Oversized or malicious files | No file upload, file fetch, or file preview surface |
| Duplicate execution and races | Read-only idempotent tools; locked atomic OAuth state updates; one-time code consumption |
| Destructive action without confirmation | No mutation tool exists in v1; annotations are accurate and not used as authorization |
| Dependency compromise | No new package dependency; repository lockfiles and audit gates remain authoritative |
| Sensitive data overcollection | Persona and registry outputs are rebuilt from privacy-reduced allowlists |
| Unauthorized public posting or messaging | No communication or open-world mutation tool exists |

## Data retention and deletion

The plugin bundle stores no user or business records. The MCP service keeps only bounded OAuth registration,
authorization transaction, code, and access-token state for operational lifetimes. Login credentials are
forwarded over TLS to Echo Auth and discarded. Operational logs retain correlation metadata and typed outcomes,
not prompts, tokens, passwords, client records, or full tool output. Token-state deletion and expiry are owned by
the existing MCP service lifecycle.

## Network and response controls

The MCP resource is stable HTTPS behind the existing gateway. Outbound destinations are configured
server-side. Requests use explicit timeouts, bounded response parsing, safe retries, strict JSON serialization,
and correlation IDs. Validation failures are client errors; dependency failures are structured upstream errors;
neither exposes stack traces or private network addresses.

The public-safety tool truthfully declares `openWorldHint: true` because state, coordinates, and filter data
cross the MCP boundary to fixed official NWS, USGS, and NASA EONET sources. That signal does not imply mutation:
`readOnlyHint` remains true and `destructiveHint` remains false.

## Security boundary that remains deliberate

The skill can describe a governed mutation workflow but cannot authorize or perform it. Any future write tool
requires a separate security review, least-privilege scope, preview/execute split, confirmation, idempotency,
audit outcome, and negative authorization coverage.
