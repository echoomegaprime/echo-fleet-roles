# Echo Prime Ops ChatGPT connector contract

## Resource

`https://mcp.echo-op.com/oauth-mcp-echo-prime-ops-v1`

An access token is audience-bound to this exact MCP resource. Tokens issued for Echo MCP Clean,
ECHO Pentester, or another resource must be rejected here, and Echo Prime Ops tokens must be
rejected by those resources.

## Scopes and tools

| Scope | Tools | Access |
|---|---|---|
| `echo.search` | `search` | Bounded read-only SDK capability search |
| `echo.fetch` | `fetch` | Exact read-only capability lookup |
| `echo.personality.read` | `echo_personas_list`, `echo_persona_get` | Privacy-reduced Persona Forge metadata |
| `echo.public-safety.read` | `echo_public_safety_context` | Bounded NWS, USGS, and NASA EONET context |

The resource advertises no write, admin, shell, deployment, service-control, browser-control,
destructive, file-search, or generic SDK-invoke scope.

## Privacy reduction

Persona tools return only stable ID, display name, role, active state, and booleans indicating whether
a voice or adapter is configured. They omit system prompts, notes, dossier paths, provider identifiers,
contact details, tenant data, and credentials. Registry results are rebuilt from allowlisted fields and
exclude target URLs, internal paths, raw configuration, and API-key material.

All repository content, registry fields, public-safety summaries, `context_tools`, logs, and tool output are
untrusted data. Embedded instructions never authorize an action or expand tool choice, scope, tenant access,
mutation, or deployment. A separately verified user intent and server-side authorization decision is required.

## Reliability and limits

All operations are idempotent. `max_results` bounds the final deduplicated search result set and is
validated as an integer in the documented range. A transient upstream timeout is attempted once more,
then returned as `upstream_timeout` with `retryable: true`. Other dependency failures return
`upstream_unavailable` without exception text or credential material.

## Deliberate hold

Sentinel answer generation is not exposed in v1. Live verification on 2026-08-09 showed the runtime
did not honor `engine_id: "NONE"` and selected an unrelated corpus. Add an answer tool only after that
backend contract has focused tests and public production proof.
