# Security report

## Scope

The security review is confined to the new Echo Prime Ops plugin, its OAuth/MCP integration points, focused
tests, package manifests, scripts, and skill resources. Unrelated dirty-worktree files are excluded.

## Implemented controls

- Strict PKCE S256; missing verifiers fail closed.
- Exact registered client and redirect binding for the Ops resource.
- Refresh-token rotation with family identifiers, used-token tombstones, and family-wide access/refresh
  revocation when a predecessor refresh token is replayed.
- One-time, expiring, attempt-limited authorization transactions and codes.
- Live Echo Auth identity verification followed by immediate temporary-session revocation.
- Required subject/email allowlist, exact resource/audience binding, tenant/role and per-tool scope checks.
- Strict input/output schemas, bounded bodies/arrays/results, deterministic safe serialization.
- Fixed upstream destinations, explicit timeouts, one bounded retry, typed errors, correlation IDs.
- Redaction of password, email, token, authorization header, cookie, login challenge, internal target/path, and
  raw configuration material, including OpenAI session/subject/organization, forwarded IP, and precise location.
- Metadata-only request tracing records method, path, content type, body length, tool name, and argument field
  names without logging argument values, credentials, headers, tokens, or personal network/location fields.
- Bounded/pruned DCR clients, login transactions, authorization codes, access tokens, and refresh tokens;
  capacity exhaustion returns 429 instead of evicting active grants. State and trace files have protected
  Windows ACLs allowing only SYSTEM and Administrators.
- The manual confidential OAuth client is disabled unless a nonempty server-side secret is configured.
- Exact production/loopback smoke endpoint allowlisting, segment-aware path confinement, strict SemVer,
  trusted executable resolution, closed package file allowlisting, random create-new temp files, and rollback.
- No write, destructive, open-world mutation, generic invoke, file search, shell, browser, or admin surface.

## Review state

Independent review findings were reproduced against the pre-remediation implementation and fixed before
release. The current 168-test focused gate covers OAuth binding/state limits, refresh-family replay, trace
redaction, package traversal, unexpected files, untrusted endpoints, temp-file safety, and marketplace rollback.
Public negative probes are included in the 53/53 protocol smoke. Formal scan
`3f69d5b8-96ad-4f01-993b-b48b47c9cf60` sealed with no validated high or critical finding in the released scope.

## Remaining medium findings

1. The active JSON store uses a process-local `RLock`; a future multi-worker deployment needs the existing
   transactional encrypted store or another inter-process transaction boundary to prevent lost updates.
2. The 256-entry login-transaction cap is fail-closed and bounded, but a privacy-preserving per-source and
   per-client limiter should run before allocation to resist temporary authorization-capacity exhaustion.
3. OAuth state is protected by private ACLs but remains plaintext in the JSON file. Migrate it to the existing
   `EncryptedOAuthStateStore` with a vault-backed key and a live-token-preserving rollback test.

The scan explicitly excluded `echo_unified_rw_sdk_mcp.py`, `resilience.py`, and
`chatgpt_pentester_plugin.py` because they belong to separate concurrently owned release scopes.
