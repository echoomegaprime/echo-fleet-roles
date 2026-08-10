[CmdletBinding()]
param(
    [ValidateRange(1024, 65535)]
    [int]$Port = 8896
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if ($PSVersionTable.PSVersion.Major -lt 7) {
    throw 'PowerShell 7 or later is required.'
}

$pluginRoot = Split-Path -Parent $PSScriptRoot
$repoRoot = Split-Path -Parent (Split-Path -Parent $pluginRoot)
. (Join-Path $PSScriptRoot 'plugin-security.ps1')
$serverPath = Join-Path $repoRoot 'GROK_BRIDGE\echo_oauth_mcp_connector.py'
if (-not (Test-Path -LiteralPath $serverPath -PathType Leaf)) {
    throw "MCP server source was not found at $serverPath"
}

$python = Resolve-TrustedApplication -Name 'python'
& $python --version | Out-Null
if ($LASTEXITCODE -ne 0) {
    throw 'Python version check failed.'
}
if (-not ($env:ECHO_OPS_ALLOWED_SUBJECTS -or $env:ECHO_OPS_ALLOWED_EMAILS)) {
    throw 'Set ECHO_OPS_ALLOWED_SUBJECTS or ECHO_OPS_ALLOWED_EMAILS before starting the protected resource.'
}

$artifactRoot = Join-Path $repoRoot 'artifacts\echo-prime-ops\runtime'
New-Item -ItemType Directory -Path $artifactRoot -Force | Out-Null
$env:ECHO_OAUTH_MCP_PORT = [string]$Port
if (-not $env:ECHO_OAUTH_STATE_PATH) {
    $env:ECHO_OAUTH_STATE_PATH = Join-Path $artifactRoot "oauth-state-$Port.json"
}
if (-not $env:ECHO_OAUTH_TRACE_PATH) {
    $env:ECHO_OAUTH_TRACE_PATH = Join-Path $artifactRoot "oauth-trace-$Port.jsonl"
}

Write-Host "Starting Echo Prime Ops staging service at http://127.0.0.1:$Port"
Write-Host 'OAuth secrets and allowlist values are not displayed.'
& $python $serverPath
if ($LASTEXITCODE -ne 0) {
    throw "MCP server exited with code $LASTEXITCODE"
}
