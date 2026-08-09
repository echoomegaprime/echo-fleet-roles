[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$RepoRoot = Split-Path -Parent $PSScriptRoot
$TempRoot = Join-Path ([IO.Path]::GetTempPath()) ("echo-role-smoke-" + [guid]::NewGuid().ToString('N'))
$StatePath = Join-Path $TempRoot 'state.sqlite3'
New-Item -ItemType Directory -Force -Path $TempRoot | Out-Null
try {
    $env:PYTHONPATH = Join-Path $RepoRoot 'src'
    $Before = python -m echo_fleet_roles --state $StatePath --json current | ConvertFrom-Json
    $Switch = python -m echo_fleet_roles --state $StatePath --json switch z --expected-current commander --idempotency-key smoke-z | ConvertFrom-Json
    $After = python -m echo_fleet_roles --state $StatePath --json current | ConvertFrom-Json
    if ($Before.role -ne 'commander' -or $Switch.context.role -ne 'reverse-engineer' -or $After.role -ne 'reverse-engineer') {
        throw 'Role switch smoke assertions failed.'
    }
    Write-Host 'Same-session role switching smoke: PASS'
}
finally {
    if (Test-Path -LiteralPath $TempRoot) { Remove-Item -LiteralPath $TempRoot -Recurse -Force }
}
