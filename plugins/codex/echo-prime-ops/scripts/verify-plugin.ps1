[CmdletBinding()]
param(
    [switch]$IncludeMcpSmoke,

    [string]$BaseUrl = 'http://127.0.0.1:8896',

    [string]$ResourceUrl = 'https://mcp.echo-op.com/oauth-mcp-echo-prime-ops-v1'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if ($PSVersionTable.PSVersion.Major -lt 7) {
    throw 'PowerShell 7 or later is required.'
}

$pluginRoot = [IO.Path]::GetFullPath((Split-Path -Parent $PSScriptRoot))
$repoRoot = Split-Path -Parent (Split-Path -Parent $pluginRoot)
. (Join-Path $PSScriptRoot 'plugin-security.ps1')
$manifestPath = Join-Path $pluginRoot '.codex-plugin\plugin.json'
$marketplacePath = Join-Path $repoRoot '.agents\plugins\marketplace.json'

foreach ($jsonPath in @($manifestPath, (Join-Path $pluginRoot '.mcp.json'), (Join-Path $pluginRoot 'chatgpt-app-submission.json'), (Join-Path $pluginRoot 'evals\golden-prompts.json'), $marketplacePath)) {
    if (-not (Test-Path -LiteralPath $jsonPath -PathType Leaf)) {
        throw "Required JSON file is missing: $jsonPath"
    }
    Get-Content -Raw -LiteralPath $jsonPath | ConvertFrom-Json | Out-Null
}

$manifest = Get-Content -Raw -LiteralPath $manifestPath | ConvertFrom-Json
Assert-StrictSemVer -Version ([string]$manifest.version)
foreach ($field in @('skills', 'mcpServers')) {
    $relative = [string]$manifest.$field
    if (-not $relative.StartsWith('./', [StringComparison]::Ordinal)) {
        throw "Manifest path $field must start with ./"
    }
    $candidate = Join-Path $pluginRoot ($relative.Substring(2).Replace('/', [IO.Path]::DirectorySeparatorChar))
    $resolved = Assert-PathUnderRoot -Root $pluginRoot -Candidate $candidate
    if (-not (Test-Path -LiteralPath $resolved)) {
        throw "Manifest path does not exist: $resolved"
    }
}

$marketplace = Get-Content -Raw -LiteralPath $marketplacePath | ConvertFrom-Json
$entry = @($marketplace.plugins | Where-Object name -eq 'echo-prime-ops')
if ($entry.Count -ne 1 -or $entry[0].source.path -ne './plugins/echo-prime-ops') {
    throw 'The local marketplace must contain exactly one valid echo-prime-ops entry.'
}

$reparsePoints = @(
    Get-Item -LiteralPath $pluginRoot -Force
    Get-ChildItem -LiteralPath $pluginRoot -Recurse -Force
) | Where-Object { $_.Attributes -band [IO.FileAttributes]::ReparsePoint }
if ($reparsePoints) {
    throw 'Plugin validation rejects symbolic links and other reparse points to prevent archive or path escape.'
}
$approvedFiles = Get-ApprovedPackageFiles -PluginRoot $pluginRoot -AllowlistPath (Join-Path $pluginRoot 'package-files.txt')

$yamlPath = Join-Path $pluginRoot 'skills\sentinel-chat-integrator\agents\openai.yaml'
$yamlText = Get-Content -Raw -LiteralPath $yamlPath
foreach ($requiredText in @('interface:', 'dependencies:', 'type: "mcp"', 'value: "echo-prime-ops"', 'allow_implicit_invocation: true')) {
    if (-not $yamlText.Contains($requiredText)) {
        throw "Skill agent YAML is missing required content: $requiredText"
    }
}

$python = Resolve-TrustedApplication -Name 'python'
& $python -m py_compile (Join-Path $repoRoot 'GROK_BRIDGE\echo_oauth_mcp_connector.py') (Join-Path $repoRoot 'GROK_BRIDGE\chatgpt_echo_prime_ops_plugin.py')
if ($LASTEXITCODE -ne 0) { throw 'Python compilation failed.' }

& $python -m pytest (Join-Path $repoRoot 'GROK_BRIDGE\tests\test_chatgpt_echo_prime_ops_plugin.py') (Join-Path $repoRoot 'GROK_BRIDGE\tests\test_echo_prime_ops_package.py') (Join-Path $repoRoot 'GROK_BRIDGE\tests\test_echo_prime_ops_script_security.py') -q
if ($LASTEXITCODE -ne 0) { throw 'Focused, package, and automation security tests failed.' }

$pluginValidator = 'C:\Users\bobmc\.codex\skills\.system\plugin-creator\scripts\validate_plugin.py'
if (Test-Path -LiteralPath $pluginValidator -PathType Leaf) {
    & $python $pluginValidator $pluginRoot
    if ($LASTEXITCODE -ne 0) { throw 'Current plugin manifest validation failed.' }
} else {
    Write-Host 'Trusted local plugin-creator validator unavailable; portable manifest and package contract checks remain enforced.'
}

$secretPattern = '(-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----|gh[pousr]_[A-Za-z0-9]{30,}|sk-[A-Za-z0-9]{32,}|AKIA[0-9A-Z]{16}|refresh[_-]?token\s*[=:])'
foreach ($file in $approvedFiles) {
    $match = Select-String -LiteralPath ([string]$file.FullName) -Pattern $secretPattern
    if ($match) {
        throw "High-confidence secret pattern detected in approved package file: $($file.Relative)"
    }
}

& (Join-Path $PSScriptRoot 'package-plugin.ps1') -SkipVerify | Out-Null
if ($LASTEXITCODE -ne 0) { throw 'Package generation failed.' }

if ($IncludeMcpSmoke) {
    Assert-TrustedMcpEndpoints -BaseUrl $BaseUrl -ResourceUrl $ResourceUrl
    & (Join-Path $PSScriptRoot 'test-mcp.ps1') -BaseUrl $BaseUrl -ResourceUrl $ResourceUrl
    if ($LASTEXITCODE -ne 0) { throw 'MCP smoke failed.' }
}

Write-Host 'Echo Prime Ops verification PASS.'
