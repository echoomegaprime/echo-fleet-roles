[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [ValidateLength(17, 256)]
    [ValidatePattern('^plugin_asdk_app[A-Za-z0-9_-]+$')]
    [string]$AppId,

    [switch]$Force
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$pluginRoot = Split-Path -Parent $PSScriptRoot
$appPath = Join-Path $pluginRoot '.app.json'
$manifestPath = Join-Path $pluginRoot '.codex-plugin\plugin.json'
if (-not (Test-Path -LiteralPath $manifestPath -PathType Leaf)) {
    throw 'Plugin manifest is missing.'
}
if ((Test-Path -LiteralPath $appPath) -and -not $Force) {
    $existing = Get-Content -Raw -LiteralPath $appPath | ConvertFrom-Json
    if ([string]$existing.apps.'echo-prime-ops'.id -match '^plugin_asdk_app') {
        throw 'A valid .app.json already exists. Use -Force only to replace it with another observed ID.'
    }
    throw 'An invalid .app.json exists. Inspect it before using -Force.'
}

$manifest = Get-Content -Raw -LiteralPath $manifestPath | ConvertFrom-Json
if ($manifest.PSObject.Properties.Name -contains 'apps' -and $manifest.apps -ne './.app.json') {
    if (-not $Force) { throw 'Manifest apps field is unexpected; use -Force only after review.' }
    $manifest.apps = './.app.json'
} elseif ($manifest.PSObject.Properties.Name -notcontains 'apps') {
    $manifest | Add-Member -NotePropertyName apps -NotePropertyValue './.app.json'
}

$appObject = [ordered]@{
    apps = [ordered]@{
        'echo-prime-ops' = [ordered]@{
            id = $AppId
            category = 'Developer Tools'
        }
    }
}
$appJson = $appObject | ConvertTo-Json -Depth 5
$manifestJson = ($manifest | ConvertTo-Json -Depth 20) + [Environment]::NewLine
$encoding = [Text.UTF8Encoding]::new($false)
$appTemp = Join-Path $pluginRoot ('.app.{0}.tmp' -f [Guid]::NewGuid().ToString('N'))
$manifestDirectory = Split-Path -Parent $manifestPath
$manifestTemp = Join-Path $manifestDirectory ('plugin.{0}.tmp' -f [Guid]::NewGuid().ToString('N'))
$appOriginal = if (Test-Path -LiteralPath $appPath -PathType Leaf) { [IO.File]::ReadAllBytes($appPath) } else { $null }
$manifestOriginal = [IO.File]::ReadAllBytes($manifestPath)
$appCommitted = $false
try {
    $appStream = [IO.File]::Open($appTemp, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
    try {
        $bytes = $encoding.GetBytes($appJson + [Environment]::NewLine)
        $appStream.Write($bytes, 0, $bytes.Length)
        $appStream.Flush($true)
    } finally { $appStream.Dispose() }

    $manifestStream = [IO.File]::Open($manifestTemp, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
    try {
        $bytes = $encoding.GetBytes($manifestJson)
        $manifestStream.Write($bytes, 0, $bytes.Length)
        $manifestStream.Flush($true)
    } finally { $manifestStream.Dispose() }

    Get-Content -Raw -LiteralPath $appTemp | ConvertFrom-Json | Out-Null
    Get-Content -Raw -LiteralPath $manifestTemp | ConvertFrom-Json | Out-Null
    Move-Item -LiteralPath $appTemp -Destination $appPath -Force
    $appCommitted = $true
    Move-Item -LiteralPath $manifestTemp -Destination $manifestPath -Force
} catch {
    if ($appCommitted) {
        if ($null -ne $appOriginal) {
            $restoreTemp = Join-Path $pluginRoot ('.app.restore.{0}.tmp' -f [Guid]::NewGuid().ToString('N'))
            try {
                $restoreStream = [IO.File]::Open($restoreTemp, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
                try {
                    $restoreStream.Write($appOriginal, 0, $appOriginal.Length)
                    $restoreStream.Flush($true)
                } finally { $restoreStream.Dispose() }
                Move-Item -LiteralPath $restoreTemp -Destination $appPath -Force
            } finally {
                if (Test-Path -LiteralPath $restoreTemp) { Remove-Item -LiteralPath $restoreTemp -Force }
            }
        } elseif (Test-Path -LiteralPath $appPath) {
            Remove-Item -LiteralPath $appPath -Force
        }
        [IO.File]::WriteAllBytes($manifestPath, $manifestOriginal)
    }
    throw
} finally {
    foreach ($temp in @($appTemp, $manifestTemp)) {
        if (Test-Path -LiteralPath $temp) { Remove-Item -LiteralPath $temp -Force }
    }
}
Write-Host 'Recorded the observed ChatGPT application ID without displaying credentials.'
