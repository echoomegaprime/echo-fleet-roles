[CmdletBinding()]
param(
    [string]$OutputDirectory = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$RepoRoot = Split-Path -Parent $PSScriptRoot
if (-not $OutputDirectory) { $OutputDirectory = Join-Path $RepoRoot 'release' }
$OutputDirectory = [IO.Path]::GetFullPath($OutputDirectory)
New-Item -ItemType Directory -Force -Path $OutputDirectory | Out-Null

pwsh -NoProfile -File (Join-Path $PSScriptRoot 'verify.ps1')
if ($LASTEXITCODE -ne 0) { throw 'Verification failed; package not created.' }

$TempRoot = Join-Path ([IO.Path]::GetTempPath()) ("echo-fleet-package-" + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Force -Path $TempRoot | Out-Null
try {
    $CodexArchive = Join-Path $OutputDirectory 'echo-fleet-role-powerpack-1.0.0.zip'
    $ClaudeArchive = Join-Path $OutputDirectory 'echo-fleet-roles-claude-2.0.0.zip'
    Compress-Archive -Path (Join-Path $RepoRoot 'plugins\codex\echo-fleet-role-powerpack\*') -DestinationPath $CodexArchive -Force
    Compress-Archive -Path (Join-Path $RepoRoot 'plugins\claude-code\echo-fleet-roles\*') -DestinationPath $ClaudeArchive -Force
    $Hashes = @($CodexArchive, $ClaudeArchive) | ForEach-Object {
        $Hash = Get-FileHash -LiteralPath $_ -Algorithm SHA256
        [pscustomobject]@{file=[IO.Path]::GetFileName($_); sha256=$Hash.Hash.ToLowerInvariant(); bytes=(Get-Item $_).Length}
    }
    $Hashes | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $OutputDirectory 'plugin-packages.sha256.json') -Encoding utf8NoBOM
    $Hashes | Format-Table -AutoSize
}
finally {
    $ResolvedTemp = [IO.Path]::GetFullPath($TempRoot)
    $AllowedRoot = [IO.Path]::GetFullPath([IO.Path]::GetTempPath())
    if ($ResolvedTemp.StartsWith($AllowedRoot, [StringComparison]::OrdinalIgnoreCase) -and (Test-Path -LiteralPath $ResolvedTemp)) {
        Remove-Item -LiteralPath $ResolvedTemp -Recurse -Force
    }
}
