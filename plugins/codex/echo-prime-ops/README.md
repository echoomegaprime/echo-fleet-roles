# Echo Prime Ops

Echo Prime Ops is a private/workspace plugin for ChatGPT and Codex. It connects to the existing
Echo OAuth MCP service and provides bounded, read-only access to the SDK registry, privacy-reduced
Persona Forge metadata, and official public-safety context.

## Architecture

This is a full plugin bundle with one focused skill and a remote tool-only MCP server. It has no
custom UI because lookup and status workflows do not gain material value from a widget. The MCP
resource uses OAuth 2.1 authorization code flow with PKCE S256, exact resource binding, minimal
per-tool scopes, a server-side subject allowlist, and structured safe errors.

## Tools

| Tool | Purpose | Scope |
|---|---|---|
| `search` | Bounded SDK capability-registry search | `echo.search` |
| `fetch` | Exact capability record lookup | `echo.fetch` |
| `echo_personas_list` | List privacy-reduced persona metadata | `echo.personality.read` |
| `echo_persona_get` | Fetch one privacy-reduced persona | `echo.personality.read` |
| `echo_public_safety_context` | Retrieve bounded NWS, USGS, and NASA EONET context | `echo.public-safety.read` |

All tools are read-only, non-destructive, idempotent, strictly validated, and useful without a UI.
Registry and persona tools are closed-world; the public-safety tool truthfully signals its read-only
interaction with fixed official providers. Sentinel answer generation, writes, generic SDK invocation, shell access, browser
control, deployment, and admin actions are unsupported in v1.

## Skill

`sentinel-chat-integrator` guides safe Sentinel integration: Persona Forge identity, tenant-side
data tools, bounded `context_tools`, failure degradation, and production verification. The MCP
server exposes the skill with `skills/list`, `skills/get`, and `resources/read` using SHA-256
digests and stable `skill://` URIs.

## Local prerequisites

- PowerShell 7
- Python 3.11 or later
- A local checkout of this repository
- Production identity allowlist supplied through environment variables

Run the complete local gate from the repository root:

```powershell
pwsh -File .\plugins\codex\echo-prime-ops\scripts\verify-plugin.ps1
```

Run the service locally after setting the required non-committed environment values:

```powershell
pwsh -File .\plugins\echo-prime-ops\scripts\run-local.ps1 -Port 8896
```

Run the protocol smoke against that endpoint:

```powershell
pwsh -File .\plugins\echo-prime-ops\scripts\test-mcp.ps1 -BaseUrl http://127.0.0.1:8896 -ResourceUrl https://mcp.echo-op.com/oauth-mcp-echo-prime-ops-v1
```

## ChatGPT connection

The production resource is connected in ChatGPT with OAuth and all five actions scanned. The observed
technical ID is `plugin_asdk_app_6a78ba0e57bc8191a51ec4b2265be152`; `.app.json` was generated from that
real host value. Follow [docs/LOCAL_TESTING.md](docs/LOCAL_TESTING.md) to refresh the connection or scan
updated tools. Never invent or hand-edit an application ID.

## Packaging and local marketplace

```powershell
pwsh -File .\plugins\echo-prime-ops\scripts\package-plugin.ps1
pwsh -File .\plugins\echo-prime-ops\scripts\install-local-marketplace.ps1
```

The repository marketplace entry is additive and does not erase other entries. Distribution is
private/workspace. Public directory readiness is tracked separately in `docs/SUBMISSION.md`.

## Deployment and rollback

The server is deployed through the existing Echo OAuth MCP service, staging-first. See
[docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for the exact gate, affected service, resource-relative
health endpoints, rollback artifact, and post-deploy proof.

## Troubleshooting and security

See [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md), [docs/AUTHENTICATION.md](docs/AUTHENTICATION.md),
and [docs/SECURITY_MODEL.md](docs/SECURITY_MODEL.md). Never paste an OAuth token, password, API key,
session cookie, client record, or private provider response into ChatGPT or a diagnostic report.

## Versioning

Tool names and required fields remain stable within major version 1. New optional fields may be
added compatibly. The MCP resource path and skill resource URIs are versioned for incompatible
changes.
