[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$RepoRoot = Split-Path -Parent $PSScriptRoot
$env:PYTHONPATH = Join-Path $RepoRoot 'src'

python -m compileall -q (Join-Path $RepoRoot 'src') (Join-Path $RepoRoot 'scripts')
if ($LASTEXITCODE -ne 0) { throw 'Python compilation failed.' }

python -m unittest discover -s (Join-Path $RepoRoot 'tests') -v
if ($LASTEXITCODE -ne 0) { throw 'Automated tests failed.' }

python (Join-Path $RepoRoot 'scripts\validate_plugins.py')
if ($LASTEXITCODE -ne 0) { throw 'Plugin contract validation failed.' }

Write-Host 'ECHO fleet roles verification: PASS'
