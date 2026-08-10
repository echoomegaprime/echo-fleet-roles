# Tool contracts

Every tool is authenticated, read-only, non-destructive, idempotent, and has
`additionalProperties: false`. Registry and persona tools are closed-world. The public-safety tool is
open-world because it reads fixed official providers, even though it has no external side effect. Every
structured result has a matching `outputSchema`.

## `search`

Use this when the user needs registered Echo SDK capabilities by exact ID, namespace, description, or
health. Do not use it for files, private paths, prompts, tenant records, or credentials.

- Input: required `query` (1–500 characters); optional `target` fixed to `sdk_caps`; `max_results` integer
  1–100, default 50; health enum `red|unknown|amber|green|unregistered`; `check_ids` and alias `cap_ids`, each
  at most 100 bounded exact IDs.
- Output: `{query,count,results[]}` with allowlisted capability/registration fields. `max_results` bounds the
  final deduplicated set.
- Scope: `echo.search`.
- Errors: `invalid_arguments`, `unauthorized`, `forbidden`, `upstream_timeout`, `upstream_unavailable`.
- Retry: once on transient timeout. No side effect or confirmation.

## `fetch`

Use this when the user needs one registered capability by exact stable ID. Do not use it for target URLs,
raw configuration, prompts, paths, or credentials.

- Input: required `id`, 1–200 characters matching letters, digits, periods, underscores, and dashes.
- Output: `{id,title,url,text,metadata:{health_status,description,source}}`; URL is the safe citation identity,
  not an internal target address.
- Scope: `echo.fetch`.
- Errors and retry: same typed policy as `search`. No side effect or confirmation.

## `echo_personas_list`

Use this when the user needs a bounded list of privacy-reduced Persona Forge identities.

- Input: `active_only` boolean, default true; `limit` integer 1–100, default 50.
- Output: `{ok,count,personas[]}`. Each persona exposes only stable ID, display name, role, active state,
  `has_voice`, and `has_adapter`.
- Scope: `echo.personality.read`.
- Errors: typed validation/auth/upstream failures. One timeout retry. No side effect or confirmation.

## `echo_persona_get`

Use this when the user needs one privacy-reduced persona by stable ID.

- Input: required `persona_id`, 1–100 characters, alphanumeric first, then alphanumeric/underscore/dash.
- Output: `{ok,persona}` using the same privacy-reduced schema.
- Scope: `echo.personality.read`.
- Errors: includes typed not-found. One timeout retry. No side effect or confirmation.

## `echo_public_safety_context`

Use this when the user needs bounded official NWS weather alerts, USGS earthquakes, or NASA EONET events.
Do not use it as an emergency dispatch service or replacement for local authorities.

- Input: optional two-letter `state`; `limit` 1–10, default 3; bounded `window`; magnitude 0–10; latitude
  -90–90; longitude -180–180; radius greater than zero and at most 1,000 km.
- Output: `{ok,count,context_tools[],freshness,generated_at}`. Context entries contain only `name` and
  bounded `summary`; freshness records fetch time and stale state by official source.
- Scope: `echo.public-safety.read`.
- Annotations: read-only true, destructive false, open-world true, idempotent true.
- Errors: typed validation/auth/upstream failures. One timeout retry. No side effect or confirmation.

## Authorization and confirmation

Each tool declares only its minimum OAuth scope. The server verifies issuer, audience/resource, signature or
opaque-token state, expiry, not-before, subject allowlist, tenant, and scope on every protected call. No v1
tool requires action confirmation because no v1 tool mutates state. Any future consequential action requires a
separate preview and execution contract, explicit scope, idempotency strategy, and confirmation.
