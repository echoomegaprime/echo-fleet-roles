[CmdletBinding()]
param(
    [string]$OutputDirectory,
    [switch]$SkipVerify
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$pluginRoot = [IO.Path]::GetFullPath((Split-Path -Parent $PSScriptRoot))
$repoRoot = Split-Path -Parent (Split-Path -Parent $pluginRoot)
. (Join-Path $PSScriptRoot 'plugin-security.ps1')

if (-not $OutputDirectory) {
    $OutputDirectory = Join-Path $repoRoot 'artifacts\plugins'
}
if (-not $SkipVerify) {
    & (Join-Path $PSScriptRoot 'verify-plugin.ps1')
    if ($LASTEXITCODE -ne 0) { throw 'Verification failed; package was not produced.' }
}

New-Item -ItemType Directory -Path $OutputDirectory -Force | Out-Null
$outputFull = [IO.Path]::GetFullPath($OutputDirectory)
[void](Assert-NoReparsePath -Path $outputFull)
$outputRelative = [IO.Path]::GetRelativePath($pluginRoot, $outputFull)
if (
    -not [IO.Path]::IsPathRooted($outputRelative) -and
    $outputRelative -ne '..' -and
    -not $outputRelative.StartsWith(('..' + [IO.Path]::DirectorySeparatorChar), [StringComparison]::Ordinal) -and
    -not $outputRelative.StartsWith(('..' + [IO.Path]::AltDirectorySeparatorChar), [StringComparison]::Ordinal)
) {
    throw 'OutputDirectory must be outside the plugin source tree.'
}

$reparsePoints = @(
    Get-Item -LiteralPath $pluginRoot -Force
    Get-ChildItem -LiteralPath $pluginRoot -Recurse -Force
) | Where-Object { $_.Attributes -band [IO.FileAttributes]::ReparsePoint }
if ($reparsePoints) {
    throw 'Packaging rejects symbolic links and other reparse points to prevent archive or path escape.'
}

$manifestPath = Join-Path $pluginRoot '.codex-plugin\plugin.json'
$manifest = Get-Content -Raw -LiteralPath $manifestPath | ConvertFrom-Json
$version = [string]$manifest.version
Assert-StrictSemVer -Version $version
$approvedFiles = Get-ApprovedPackageFiles -PluginRoot $pluginRoot -AllowlistPath (Join-Path $pluginRoot 'package-files.txt')

$archiveName = "echo-prime-ops-$version.zip"
$archivePath = Assert-PathUnderRoot -Root $outputFull -Candidate (Join-Path $outputFull $archiveName)
$hashPath = Assert-PathUnderRoot -Root $outputFull -Candidate "$archivePath.sha256"
$metadataPath = Assert-PathUnderRoot -Root $outputFull -Candidate (Join-Path $outputFull 'echo-prime-ops-package-metadata.json')
$tempPath = Assert-PathUnderRoot -Root $outputFull -Candidate (Join-Path $outputFull ('.echo-prime-ops.{0}.tmp' -f [Guid]::NewGuid().ToString('N')))
[void](Assert-NoReparsePath -Path $outputFull)

Add-Type -AssemblyName System.IO.Compression
$fileHashes = [ordered]@{}
try {
    $stream = [IO.File]::Open($tempPath, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
    try {
        $zip = [IO.Compression.ZipArchive]::new($stream, [IO.Compression.ZipArchiveMode]::Create, $true)
        try {
            foreach ($file in $approvedFiles) {
                $entryName = [string]$file.Relative
                $fullName = Assert-PathUnderRoot -Root $pluginRoot -Candidate ([string]$file.FullName)
                $item = Get-Item -LiteralPath $fullName -Force
                if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) {
                    throw "Approved package file is a reparse point: $entryName"
                }
                $fileHashes[$entryName] = (Get-FileHash -LiteralPath $fullName -Algorithm SHA256).Hash.ToLowerInvariant()
                $entry = $zip.CreateEntry($entryName, [IO.Compression.CompressionLevel]::Optimal)
                $entry.LastWriteTime = [DateTimeOffset]::new(2000, 1, 1, 0, 0, 0, [TimeSpan]::Zero)
                $input = [IO.File]::Open($fullName, [IO.FileMode]::Open, [IO.FileAccess]::Read, [IO.FileShare]::Read)
                try {
                    $output = $entry.Open()
                    try { $input.CopyTo($output) } finally { $output.Dispose() }
                } finally { $input.Dispose() }
            }
        } finally { $zip.Dispose() }
    } finally { $stream.Dispose() }

    Move-Item -LiteralPath $tempPath -Destination $archivePath -Force
} finally {
    if (Test-Path -LiteralPath $tempPath) { Remove-Item -LiteralPath $tempPath -Force }
}

$hash = (Get-FileHash -LiteralPath $archivePath -Algorithm SHA256).Hash.ToLowerInvariant()
[IO.File]::WriteAllText($hashPath, "$hash  $archiveName$([Environment]::NewLine)", [Text.UTF8Encoding]::new($false))
$metadata = [ordered]@{
    name = $manifest.name
    version = $version
    archive = $archiveName
    sha256 = $hash
    files = $fileHashes
    generated_at = [DateTime]::UtcNow.ToString('o')
}
[IO.File]::WriteAllText($metadataPath, (($metadata | ConvertTo-Json -Depth 5) + [Environment]::NewLine), [Text.UTF8Encoding]::new($false))
Write-Output $archivePath
