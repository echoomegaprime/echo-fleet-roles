[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$pluginRoot = [IO.Path]::GetFullPath((Split-Path -Parent $PSScriptRoot))
$repoRoot = [IO.Path]::GetFullPath((Split-Path -Parent (Split-Path -Parent $pluginRoot)))
$marketplacePath = Join-Path $repoRoot '.agents\plugins\marketplace.json'
$manifestPath = Join-Path $pluginRoot '.codex-plugin\plugin.json'

& (Join-Path $PSScriptRoot 'verify-plugin.ps1')
if ($LASTEXITCODE -ne 0) { throw 'Plugin verification failed; no Codex configuration was changed.' }

foreach ($path in @($marketplacePath, $manifestPath)) {
    Get-Content -Raw -LiteralPath $path | ConvertFrom-Json | Out-Null
}
$marketplace = Get-Content -Raw -LiteralPath $marketplacePath | ConvertFrom-Json
$entry = @($marketplace.plugins | Where-Object name -eq 'echo-prime-ops')
if ($entry.Count -ne 1 -or $entry[0].source.path -ne './plugins/echo-prime-ops') {
    throw 'The repo-scoped marketplace entry is missing or invalid.'
}

$node = 'C:\Program Files\nodejs\node.exe'
$codexEntrypoint = 'C:\cx\node_modules\@openai\codex\bin\codex.js'
foreach ($trustedPath in @($node, $codexEntrypoint)) {
    if (-not (Test-Path -LiteralPath $trustedPath -PathType Leaf)) {
        throw "Trusted Codex launcher component is missing: $trustedPath"
    }
}

$listText = (& $node $codexEntrypoint plugin marketplace list --json | Out-String)
if ($LASTEXITCODE -ne 0) { throw 'Unable to inspect existing Codex marketplaces.' }
$configured = $listText | ConvertFrom-Json
$existing = @($configured.marketplaces | Where-Object name -eq 'echo-omega-prime')
if ($existing.Count -gt 1) { throw 'Multiple echo-omega-prime marketplace entries require manual inspection.' }
if ($existing.Count -eq 1 -and [IO.Path]::GetFullPath([string]$existing[0].root) -ne $repoRoot) {
    throw 'An echo-omega-prime marketplace already points to a different root.'
}

$pluginsBeforeText = (& $node $codexEntrypoint plugin list --json | Out-String)
if ($LASTEXITCODE -ne 0) { throw 'Unable to inspect installed Codex plugins.' }
$pluginsBefore = $pluginsBeforeText | ConvertFrom-Json
$pluginWasInstalled = @($pluginsBefore.installed | Where-Object pluginId -eq 'echo-prime-ops@echo-omega-prime').Count -eq 1
$marketplaceWasInstalled = $existing.Count -eq 1

try {
    if (-not $marketplaceWasInstalled) {
        & $node $codexEntrypoint plugin marketplace add $repoRoot --json
        if ($LASTEXITCODE -ne 0) { throw 'Codex marketplace registration failed.' }
    }
    & $node $codexEntrypoint plugin add 'echo-prime-ops@echo-omega-prime' --json
    if ($LASTEXITCODE -ne 0) { throw 'Codex plugin installation failed.' }
} catch {
    $originalError = $_
    $rollbackProblems = [Collections.Generic.List[string]]::new()

    $pluginsNowText = (& $node $codexEntrypoint plugin list --json | Out-String)
    if ($LASTEXITCODE -eq 0) {
        $pluginsNow = $pluginsNowText | ConvertFrom-Json
        $pluginIsInstalled = @($pluginsNow.installed | Where-Object pluginId -eq 'echo-prime-ops@echo-omega-prime').Count -eq 1
        if (-not $pluginWasInstalled -and $pluginIsInstalled) {
            & $node $codexEntrypoint plugin remove 'echo-prime-ops@echo-omega-prime' --json | Out-Null
            if ($LASTEXITCODE -ne 0) { $rollbackProblems.Add('plugin removal failed') }
        }
    } else {
        $rollbackProblems.Add('plugin state inspection failed')
    }

    $marketsNowText = (& $node $codexEntrypoint plugin marketplace list --json | Out-String)
    if ($LASTEXITCODE -eq 0) {
        $marketsNow = $marketsNowText | ConvertFrom-Json
        $marketplaceIsInstalled = @($marketsNow.marketplaces | Where-Object name -eq 'echo-omega-prime').Count -eq 1
        if (-not $marketplaceWasInstalled -and $marketplaceIsInstalled) {
            & $node $codexEntrypoint plugin marketplace remove 'echo-omega-prime' --json | Out-Null
            if ($LASTEXITCODE -ne 0) { $rollbackProblems.Add('marketplace removal failed') }
        }
    } else {
        $rollbackProblems.Add('marketplace state inspection failed')
    }

    $pluginsAfterText = (& $node $codexEntrypoint plugin list --json | Out-String)
    $marketsAfterText = (& $node $codexEntrypoint plugin marketplace list --json | Out-String)
    if ($LASTEXITCODE -ne 0) {
        $rollbackProblems.Add('rollback verification failed')
    } else {
        $pluginsAfter = $pluginsAfterText | ConvertFrom-Json
        $marketsAfter = $marketsAfterText | ConvertFrom-Json
        $pluginAfter = @($pluginsAfter.installed | Where-Object pluginId -eq 'echo-prime-ops@echo-omega-prime').Count -eq 1
        $marketAfter = @($marketsAfter.marketplaces | Where-Object name -eq 'echo-omega-prime').Count -eq 1
        if ($pluginAfter -ne $pluginWasInstalled -or $marketAfter -ne $marketplaceWasInstalled) {
            $rollbackProblems.Add('installation rollback did not restore the original Codex configuration')
        }
    }
    if ($rollbackProblems.Count -gt 0) {
        throw "Plugin installation failed and installation rollback did not restore the original Codex configuration: $($rollbackProblems -join '; ')"
    }
    throw $originalError
}
Write-Host 'Local marketplace and Echo Prime Ops plugin installed. Refresh the current Codex host to load new capabilities.'
