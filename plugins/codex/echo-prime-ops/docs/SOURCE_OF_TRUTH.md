# Source of truth

Checked 2026-08-09T05:30:00Z against the current official OpenAI developer documentation.

## Official pages reviewed

- `plugins/build/app-quickstart`
- `plugins/plan/tools`
- `plugins/build/mcp-server`
- `plugins/build/chatgpt-ui`
- `plugins/build/auth`
- `plugins/build/skills`
- `plugins/build/plugins`
- `plugins/deploy/connect-chatgpt`
- `plugins/deploy/submission`
- `plugins/deploy/app-review`
- `plugins/deploy/submission-errors`
- `plugins/guides/security-privacy`
- `plugins/guides/optimize-metadata`
- `plugins/reference`
- `plugins/app-guidelines`
- `api/docs/guides/secure-mcp-tunnels`

## Examples examined

The minimal official Apps SDK MCP server quickstart and the closest MCP Apps
`@modelcontextprotocol/ext-apps` example were inspected. The current example dependency snapshot used
`@modelcontextprotocol/sdk` 1.20.2, `@modelcontextprotocol/ext-apps` 1.0.1, and Zod 3.25.76. This
repository already has a compatible Python standard-library Streamable HTTP MCP/OAuth runtime, so the
implementation preserved that runtime and added no unnecessary JavaScript dependency.

## Decisions grounded in current documentation

- A tool-only MCP application is correct for lookup and status workflows; no UI was added.
- The distributable bundle is rooted at `.codex-plugin/plugin.json`, not the obsolete OpenAPI-only
  plugin format.
- Every tool has strict input and output schemas, explicit safety annotations, and a minimal OAuth
  security scheme.
- Private data requires OAuth authorization code flow with PKCE S256, protected-resource metadata,
  exact resource binding, and server-side authorization.
- Skills are declared through `capabilities.extensions["io.modelcontextprotocol/skills"]` and exposed
  with `skills/list`, `skills/get`, and `resources/read` using stable `skill://` URIs and SHA-256 digests.
- ChatGPT connection uses current developer mode under Settings, Apps & Connectors, Create, followed by
  authentication and Scan Tools.
- Secure MCP Tunnel is suitable for private development, not a public submission endpoint.

## Compatibility decisions

The existing Echo OAuth MCP service, JSON-RPC envelope, Python test harness, and public MCP hostname were
retained. Existing connector paths remain untouched. A new versioned resource path isolates this plugin's
tokens, scopes, tools, and metadata. No legacy Custom GPT Action or OpenAPI-only manifest was created.

## Current host limitation

A real ChatGPT-generated `plugin_asdk_app...` identifier can exist only after the MCP resource is connected
in a supported ChatGPT account. The package therefore omits `.app.json` until that value is observed and
provides a strict atomic configurator. Public-directory submission also requires organization and portal
state that cannot be represented truthfully by code alone.
