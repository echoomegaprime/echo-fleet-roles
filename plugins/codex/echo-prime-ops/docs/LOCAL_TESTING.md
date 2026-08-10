# Local and ChatGPT testing

## Local verification

From the repository root in PowerShell 7:

```powershell
pwsh -File .\plugins\codex\echo-prime-ops\scripts\verify-plugin.ps1
```

To launch a staging instance, set an authorized identity allowlist in the process environment, then run:

```powershell
pwsh -File .\plugins\codex\echo-prime-ops\scripts\run-local.ps1 -Port 8896
```

For the full OAuth smoke, put a dedicated authorized test identity into `ECHO_OPS_TEST_EMAIL` and
`ECHO_OPS_TEST_PASSWORD` in the process environment. The smoke does not print either value:

```powershell
pwsh -File .\plugins\echo-prime-ops\scripts\test-mcp.ps1 -BaseUrl http://127.0.0.1:8896 -ResourceUrl https://mcp.echo-op.com/oauth-mcp-echo-prime-ops-v1
```

The protocol test verifies discovery, DCR, PKCE, token binding, initialize, tools/list, unauthorized and
wrong-resource failures, skill resources/digests, and every safe tool.

## ChatGPT developer-mode connection

Use the current documented path, not the retired personal-plugins page:

1. Open ChatGPT Settings.
2. Open Apps & Connectors and enable developer mode if the account exposes it.
3. Select Create and enter `https://mcp.echo-op.com/oauth-mcp-echo-prime-ops-v1`.
4. Complete Echo Auth as an allowlisted identity.
5. Select Scan Tools and verify the exact five-tool inventory.
6. Start a new chat and run direct, indirect, negative, authorization, repeat-call, and error-recovery cases.

If ChatGPT exposes a real technical ID beginning with `plugin_asdk_app`, record it atomically:

```powershell
pwsh -File .\plugins\echo-prime-ops\scripts\configure-app-id.ps1 -AppId 'plugin_asdk_app_REAL_VALUE'
```

The script rejects other formats and will not overwrite an existing valid mapping unless `-Force` is supplied.
After metadata changes, refresh the connection and run Scan Tools again; cached metadata is not proof of the
current server.

## Local marketplace

```powershell
pwsh -File .\plugins\echo-prime-ops\scripts\install-local-marketplace.ps1
```

The script validates the root marketplace and plugin paths, then adds the local marketplace and plugin through
the current Codex CLI. It does not erase unrelated marketplace configuration. Restart or refresh the host only
when its current plugin workflow requires it; a system reboot is never part of this plugin procedure.

## Accurate host evidence

A healthy endpoint, tools/list, or a generated `.app.json` is insufficient. Host integration is PASS only when
the plugin is observed in a supported ChatGPT surface and a real tool invocation returns the expected result.
If developer mode, the registration ID, or an account feature is unavailable, record
`BLOCKED BY EXTERNAL DEPENDENCY` rather than weakening the MCP server.
