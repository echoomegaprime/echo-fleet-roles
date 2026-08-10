# Troubleshooting

Run diagnostics from PowerShell 7. Never paste credentials or bearer tokens into a command transcript.

## MCP initialization failure

- Symptom: initialize returns no server identity or a transport error.
- Likely causes: service stopped, wrong path, tunnel route failure, or stale process.
- Diagnostic: `Invoke-RestMethod https://mcp.echo-op.com/oauth-mcp-echo-prime-ops-v1/version`.
- Expected evidence: JSON identifying `echo-prime-ops` version 1.0.0.
- Correction: verify the candidate on staging, then restart only `EchoOAuthMCP`; do not reboot.

## Tool scan failure or schema mismatch

- Symptom: ChatGPT cannot scan tools or shows an old/extra tool.
- Likely causes: cached connection metadata, wrong MCP path, stale service artifact, or invalid schema.
- Diagnostic: run `scripts/test-mcp.ps1` and compare the exact five-tool inventory.
- Expected evidence: search, fetch, two persona tools, and public-safety context only.
- Correction: repair schema/runtime parity, redeploy through staging, then Refresh or Scan Tools in a new chat.

## OAuth discovery failure

- Symptom: the host never opens authorization.
- Likely causes: protected-resource metadata unavailable, issuer mismatch, TLS/routing failure.
- Diagnostic: `Invoke-RestMethod https://mcp.echo-op.com/.well-known/oauth-protected-resource/oauth-mcp-echo-prime-ops-v1`.
- Expected evidence: exact resource URL, authorization server, and four read scopes.
- Correction: restore gateway route or metadata; never substitute another connector's resource.

## OAuth redirect mismatch

- Symptom: authorization returns `invalid_request` for the callback.
- Likely causes: callback differs from registered DCR/CIMD metadata or stale client registration.
- Diagnostic: inspect sanitized server audit metadata for client ID and redirect match, not the authorization code.
- Expected evidence: exact HTTPS redirect present in the registered client.
- Correction: register the exact host callback and retry a fresh authorization transaction.

## Missing scope

- Symptom: one tool returns forbidden while others work.
- Likely causes: the access token lacks that tool's minimum scope or cached authorization predates metadata.
- Diagnostic: run the unauthorized/scope tests in the focused test suite.
- Expected evidence: typed forbidden result and OAuth challenge naming the minimum scope.
- Correction: reconnect and consent to the published read scope; do not widen other scopes.

## Wrong token audience

- Symptom: a token works on another Echo connector but fails here, or vice versa.
- Likely cause: expected resource binding is working or the host requested the wrong resource.
- Diagnostic: run the smoke test's `resource_bound_token_rejected_elsewhere` check.
- Expected evidence: cross-resource call is rejected without HTTP 500.
- Correction: request a fresh token for the exact Echo Prime Ops resource.

## Failed JWKS retrieval

- Symptom: identity verification fails after login in a JWT-backed deployment.
- Likely causes: identity-provider outage, issuer mismatch, TLS failure, or expired cache.
- Diagnostic: retrieve the configured issuer's discovery/JWKS endpoint from the service host and inspect status only.
- Expected evidence: valid JSON key set from the configured issuer.
- Correction: restore identity-provider reachability; fail closed until signature verification is available.

## UI not rendering, CSP rejection, or widget bridge failure

- Symptom: the user expects a widget, but no component appears.
- Likely cause: this is intentionally a tool-only v1 plugin.
- Diagnostic: inspect `.codex-plugin/plugin.json` and verify it has no `apps` field or UI resource.
- Expected evidence: tool-only MCP bundle with model-readable structured output.
- Correction: use the tool response. Add UI only under a separately specified workflow that materially needs it.

## Missing `plugin_asdk_app` ID

- Symptom: `.app.json` is absent.
- Likely cause: the production resource has not yet yielded a real ChatGPT technical ID.
- Diagnostic: inspect the connected application in current ChatGPT developer mode.
- Expected evidence: a real ID beginning with `plugin_asdk_app`.
- Correction: run `scripts/configure-app-id.ps1` with that observed ID; never invent one.

## Local marketplace plugin missing

- Symptom: Codex cannot find `echo-prime-ops`.
- Likely causes: invalid root marketplace path, plugin manifest parse failure, or host metadata cache.
- Diagnostic: `pwsh -File .\plugins\echo-prime-ops\scripts\install-local-marketplace.ps1`.
- Expected evidence: manifest/path validation passes and the CLI reports the marketplace/plugin operation.
- Correction: repair only the invalid entry, rerun the installer, then refresh the Codex plugin host.

## Unsupported write tool on the current ChatGPT plan

- Symptom: the user expects mutation but tools/list contains only reads.
- Likely cause: v1 intentionally exposes no write tool, independent of account plan.
- Diagnostic: inspect `docs/TOOL_CONTRACTS.md` and public tools/list.
- Expected evidence: five read-only tools with no destructive/open-world action.
- Correction: use the governed SOL/operator workflow; do not weaken this connector.

## Temporary tunnel failure

- Symptom: a development tunnel URL is unreachable.
- Likely causes: tunnel process stopped, host sleep, expired route, or wrong local port.
- Diagnostic: check the tunnel process and local resource-relative `/healthz` separately.
- Expected evidence: local health green and tunnel route mapped to the same port.
- Correction: restart only the development tunnel. Do not treat it as a production endpoint.

## Production endpoint timeout

- Symptom: public MCP calls time out while local staging works.
- Likely causes: gateway route, service supervisor, upstream dependency, or firewall issue.
- Diagnostic: compare public `/readyz`, local `/readyz`, service status, and correlation-matched logs.
- Expected evidence: the first failing hop is isolated without credential material.
- Correction: repair that hop; roll back the connector if the candidate caused the failure.

## Submission validation error

- Symptom: the OpenAI portal rejects metadata or a test case.
- Likely causes: current portal schema changed, missing organization/policy URL, or mismatch with live tools.
- Diagnostic: compare the current official submission documentation, public tools/list, and internal submission JSON.
- Expected evidence: exact field or tool mismatch identified.
- Correction: update truthful metadata and rescan. Do not fabricate an external value to satisfy validation.
