[CmdletBinding()]
param(
    [switch]$InstallRuntime
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$RepoRoot = Split-Path -Parent $PSScriptRoot
python (Join-Path $RepoRoot 'scripts\validate_plugins.py')
if ($LASTEXITCODE -ne 0) { throw 'Refusing to install an invalid plugin bundle.' }

codex plugin marketplace add $RepoRoot
if ($LASTEXITCODE -ne 0) { throw 'Codex marketplace registration failed.' }

if ($InstallRuntime) {
    python -m pip install --user $RepoRoot
    if ($LASTEXITCODE -ne 0) { throw 'Role runtime installation failed.' }
}

Write-Host 'Marketplace registered. Restart Codex once to discover and trust the plugin hooks.'
