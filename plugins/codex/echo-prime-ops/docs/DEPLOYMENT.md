# Deployment

## Topology

ChatGPT/Codex → `https://mcp.echo-op.com/oauth-mcp-echo-prime-ops-v1` → existing Cloudflare tunnel →
HAMMER `EchoOAuthMCP` service on loopback port 8796 → Echo SDK registry, Persona Forge, public-safety adapter,
and Echo Auth. Connector names and existing MCP routes remain unchanged.

## Production gate

1. Record current repository commit, deployed file SHA-256, service configuration, and health.
2. Preserve an exact rollback copy of the deployed connector.
3. Set `ECHO_OPS_ALLOWED_SUBJECTS` from the live Echo Auth subject without printing it. Preserve all existing
   OAuth, rate-limit, audit, gateway, and connector settings.
4. Boot the exact candidate code on staging port 8896 using the production resource URL.
5. Run syntax, focused tests, package tests, full relevant tests, security scan, OAuth smoke, every safe tool,
   wrong-resource, wrong-verifier, unauthorized, and readiness probes.
6. Promote only after staging is green. Restart only `EchoOAuthMCP`; do not reboot the workstation.
7. Verify resource-relative `/healthz`, `/readyz`, `/version`, discovery, initialize, tools/list, and live calls
   through the public endpoint.
8. Audit the existing custom connectors with read-only calls and inspect logs for 500s, schema drift, argument
   mutation, or credential leakage.

## Rollback

The syntax-verified rollback connector is preserved in the operator's private evidence archive
(artifact `chatgpt_echo_prime_ops_20260809T142636Z/echo_oauth_mcp_connector.py.rollback`)
with SHA-256 `B4084D4485025E6B9733023FE6EC261DE5D85AAF797F09A4A5E12937FD208157`.
Rollback restores that exact file to the deployed connector path, validates its hash and syntax, boots it on
staging, then restarts only `EchoOAuthMCP`. Existing routes are verified after rollback. The rollback artifact
does not contain environment secrets.

## Deployed evidence

- Candidate source SHA-256: `4D7DF492F931EBC56928159DCADFF463648D4CF4CA477EA8DFC9548FB3A0C4C5`.
- Supervisor: `EchoOAuthMCP`; scoped service restart changed the Python listener PID from 38456 to 31964 on
  loopback port 8796.
- Public route: `https://mcp.echo-op.com/oauth-mcp-echo-prime-ops-v1`.
- Public acceptance: 53/53 checks passed after the final deployment. Health=`alive`, readiness=`ready`, and
  version=`1.0.0`. State/trace ACLs remained protected with zero broad allow entries, and the recent trace sample
  contained zero sensitive-value patterns. No workstation reboot occurred.

## Container posture

Not applicable. The affected production unit is an existing Windows service; introducing a competing
container would add an unnecessary deployment path. Its current supervisor, tunnel, and secret-management
mechanisms are preserved.

## Versioning

The resource path is versioned. Tool names, required fields, scopes, and output identities remain stable within
v1. Compatible optional fields may be added; incompatible changes require a new resource version and a fresh
ChatGPT scan.
