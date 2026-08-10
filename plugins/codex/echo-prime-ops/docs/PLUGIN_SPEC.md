# Plugin specification

## Product identity

- Name and machine identifier: Echo Prime Ops / `echo-prime-ops`
- Description: read-only operational discovery for the Echo SDK registry, Persona Forge, and official
  public-safety context.
- Intended users: the Commander and authorized Echo workspace operators using ChatGPT or Codex.
- Audience: Private/workspace.
- Category: Developer Tools.
- Surfaces: ChatGPT Apps & Connectors and Codex plugin installation.
- Authentication: authenticated use only.
- Archetype: Full plugin bundle composed of one focused skill and a remote tool-only MCP server.
- UI: No custom UI. Concise lookup and status results are fully useful in model-readable structured output.

## User goals and workflows

### Capability discovery

The user asks which Echo capability implements an operation, whether an exact capability is registered, or
which capabilities match a namespace or health. Direct prompts include “find echo.a2a.health”; indirect
prompts include “which Echo endpoint reports A2A health?” The plugin reads the SDK registry and returns a
bounded, deterministic, privacy-reduced result. It never searches files or reveals target URLs. Scope:
`echo.search` or `echo.fetch`. Failure is a typed validation or upstream error; retry occurs once only for a
transient timeout. UI is unnecessary.

### Persona discovery

The user asks which Persona Forge identities are active or requests one by stable ID. The plugin returns
display identity, role, active state, and configured/not-configured booleans. It does not return prompts,
notes, paths, voice identifiers, provider details, or tenant data. Scope: `echo.personality.read`. UI is
unnecessary.

### Public-safety context

The user asks for bounded official weather-alert, earthquake, or EONET context for a state or geographic
radius. The plugin returns Sentinel-ready summaries plus freshness metadata. It is not emergency dispatch or
a substitute for local authorities. Scope: `echo.public-safety.read`. UI is unnecessary.

### Sentinel integration guidance

The user asks to add, migrate, harden, or verify an Echo Sentinel integration. The skill guides repository
inspection, Persona Forge use, tenant-side data authorization, bounded `context_tools`, staging, and live
verification. Mutations remain on the governed operator path and are not granted by this plugin.

## Non-goals

- Generic SDK invocation, shell execution, service control, deployment, browser control, admin work, file
  search, tenant database access, and any destructive operation.
- Sentinel answer generation until its `engine_id: "NONE"` behavior passes its own production contract.
- Emergency response, dispatch, medical advice, or replacing official local instructions.
- Durable persona definitions outside Persona Forge.
- Custom UI, public posting, messaging, or any write operation.

## Data classification

| Data | Classification | Storage |
|---|---|---|
| Capability ID, title, description, health | Internal | Not stored by plugin |
| Persona ID, display name, role, active/configured booleans | Internal | Not stored by plugin |
| Official NWS/USGS/EONET summaries and freshness | Public | Upstream cache only |
| OAuth authorization code and access token | Authentication data | Server state only, bounded lifetime |
| Email and password during login | Authentication data, prohibited from logs/storage | Forwarded to Echo Auth and discarded |
| System prompts, notes, paths, provider IDs, tenant data | Confidential, prohibited from output | Never returned |
| Correlation ID, status, latency, typed error code | Internal telemetry | Structured operational logs |

## Operational requirements

- Availability target: 99.9% monthly for the MCP edge, excluding upstream provider outages.
- Latency target: registry/persona p95 under 3 seconds; public-safety p95 under 10 seconds.
- Timeouts: explicit per upstream; one bounded retry only for transient timeouts.
- Idempotency: every v1 tool is read-only and retry-safe.
- Limits: request body caps, strict schemas, `max_results` 1–100, persona list 1–100, safety results 1–10.
- Rate limiting: existing MCP service controls remain in force; no bypass is added.
- Persistence: OAuth registration, one-time code, and bounded token state only; no authoritative business data
  in process memory.
- Retention: authorization transactions expire in five minutes; access tokens expire per server policy;
  sensitive credential fields are neither logged nor retained.
- Audit: correlation-aware authentication and tool outcome metadata without payload secrets.
- Deployment: existing Echo OAuth MCP Windows service behind the production Cloudflare tunnel.
- Rollback: restore the recorded connector artifact and restart only that service after staging verification.
