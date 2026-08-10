[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [ValidatePattern('^https?://')]
    [string]$BaseUrl,

    [ValidatePattern('^https://')]
    [string]$ResourceUrl = 'https://mcp.echo-op.com/oauth-mcp-echo-prime-ops-v1',

    [ValidateRange(2, 180)]
    [int]$TimeoutSeconds = 45,

    [switch]$SkipLiveTools
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if ($PSVersionTable.PSVersion.Major -lt 7) {
    throw 'PowerShell 7 or later is required.'
}
if (-not $env:ECHO_OPS_TEST_EMAIL -or -not $env:ECHO_OPS_TEST_PASSWORD) {
    throw 'Set ECHO_OPS_TEST_EMAIL and ECHO_OPS_TEST_PASSWORD in the process environment. Values are never printed.'
}

$pluginRoot = Split-Path -Parent $PSScriptRoot
$repoRoot = Split-Path -Parent (Split-Path -Parent $pluginRoot)
. (Join-Path $PSScriptRoot 'plugin-security.ps1')
Assert-TrustedMcpEndpoints -BaseUrl $BaseUrl -ResourceUrl $ResourceUrl
$smokePath = Join-Path $repoRoot 'GROK_BRIDGE\tests\smoke_echo_prime_ops_mcp.py'
$connectorPath = Join-Path $repoRoot 'GROK_BRIDGE\echo_oauth_mcp_connector.py'
Assert-TrustedLoopbackMcpProcess -BaseUrl $BaseUrl -ExpectedScript $connectorPath
if (-not (Test-Path -LiteralPath $smokePath -PathType Leaf)) {
    throw "MCP smoke client was not found at $smokePath"
}

$arguments = @(
    $smokePath,
    '--base-url', $BaseUrl.TrimEnd('/'),
    '--resource-url', $ResourceUrl,
    '--timeout', [string]$TimeoutSeconds
)
if ($SkipLiveTools) {
    $arguments += '--skip-live-tools'
}

$python = Resolve-TrustedApplication -Name 'python'
& $python @arguments
if ($LASTEXITCODE -ne 0) {
    throw "MCP protocol smoke failed with code $LASTEXITCODE"
}
