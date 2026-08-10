Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Assert-PathUnderRoot {
    [CmdletBinding()]
    [OutputType([string])]
    param(
        [Parameter(Mandatory)][string]$Root,
        [Parameter(Mandatory)][string]$Candidate
    )

    $rootFull = [IO.Path]::GetFullPath($Root).TrimEnd(
        [IO.Path]::DirectorySeparatorChar,
        [IO.Path]::AltDirectorySeparatorChar
    )
    $candidateFull = [IO.Path]::GetFullPath($Candidate)
    $relative = [IO.Path]::GetRelativePath($rootFull, $candidateFull)
    $parentPrefix = '..' + [IO.Path]::DirectorySeparatorChar
    $altParentPrefix = '..' + [IO.Path]::AltDirectorySeparatorChar
    if (
        [IO.Path]::IsPathRooted($relative) -or
        $relative -eq '..' -or
        $relative.StartsWith($parentPrefix, [StringComparison]::Ordinal) -or
        $relative.StartsWith($altParentPrefix, [StringComparison]::Ordinal)
    ) {
        throw "Path escapes the approved root: $Candidate"
    }
    return $candidateFull
}

function Assert-NoReparsePath {
    [CmdletBinding()]
    [OutputType([string])]
    param([Parameter(Mandatory)][string]$Path)

    $resolved = [IO.Path]::GetFullPath($Path)
    $cursor = Get-Item -LiteralPath $resolved -Force -ErrorAction Stop
    while ($null -ne $cursor) {
        if ($cursor.Attributes -band [IO.FileAttributes]::ReparsePoint) {
            throw "Reparse points are not allowed in this release path: $($cursor.FullName)"
        }
        $parent = Split-Path -Parent $cursor.FullName
        if (-not $parent -or $parent -eq $cursor.FullName -or -not (Test-Path -LiteralPath $parent)) {
            break
        }
        $cursor = Get-Item -LiteralPath $parent -Force -ErrorAction Stop
    }
    return $resolved
}

function Assert-StrictSemVer {
    [CmdletBinding()]
    param([Parameter(Mandatory)][string]$Version)

    if ($Version.Length -gt 96 -or $Version -notmatch '^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$') {
        throw 'Plugin version must be a bounded semantic version.'
    }
}

function Resolve-TrustedApplication {
    [CmdletBinding()]
    [OutputType([string])]
    param([Parameter(Mandatory)][string]$Name)

    $applicationName = if ($Name.EndsWith('.exe', [StringComparison]::OrdinalIgnoreCase)) {
        $Name
    } else {
        "$Name.exe"
    }
    $command = Get-Command -Name $applicationName -CommandType Application -ErrorAction Stop |
        Select-Object -First 1
    $resolved = [IO.Path]::GetFullPath(
        (Resolve-Path -LiteralPath ([string]$command.Source) -ErrorAction Stop).Path
    )
    if ([IO.Path]::GetExtension($resolved) -ne '.exe') {
        throw "Resolved command is not a native application: $Name"
    }

    $trustedRoots = if ($IsWindows) {
        @(
            [Environment]::GetFolderPath([Environment+SpecialFolder]::ProgramFiles),
            [Environment]::GetFolderPath([Environment+SpecialFolder]::ProgramFilesX86),
            [Environment]::GetFolderPath([Environment+SpecialFolder]::System)
        ) | Where-Object { $_ }
    } else {
        @('/usr/bin', '/usr/local/bin', '/opt/homebrew/bin')
    }
    $trusted = $false
    foreach ($root in $trustedRoots) {
        try {
            [void](Assert-PathUnderRoot -Root $root -Candidate $resolved)
            $trusted = $true
            break
        } catch {
            continue
        }
    }
    if (-not $trusted) {
        throw "Resolved command is outside the trusted application roots: $Name"
    }
    return $resolved
}

function Assert-TrustedMcpEndpoints {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$BaseUrl,
        [Parameter(Mandatory)][string]$ResourceUrl
    )

    $base = $null
    if (-not [Uri]::TryCreate($BaseUrl, [UriKind]::Absolute, [ref]$base)) {
        throw 'BaseUrl must be an absolute URI.'
    }
    if ($base.UserInfo -or $base.Query -or $base.Fragment -or $base.AbsolutePath -ne '/') {
        throw 'BaseUrl must be a credential-free origin without a path, query, or fragment.'
    }
    $trustedProduction = (
        $base.Scheme -eq 'https' -and
        $base.DnsSafeHost -eq 'mcp.echo-op.com' -and
        $base.IsDefaultPort
    )
    $trustedLoopback = $base.Scheme -eq 'http' -and $base.IsLoopback
    if (-not ($trustedProduction -or $trustedLoopback)) {
        throw 'BaseUrl must be loopback HTTP or the exact production HTTPS origin.'
    }

    $expectedResource = 'https://mcp.echo-op.com/oauth-mcp-echo-prime-ops-v1'
    if (-not [string]::Equals($ResourceUrl, $expectedResource, [StringComparison]::Ordinal)) {
        throw 'ResourceUrl must equal the registered Echo Prime Ops OAuth resource.'
    }
}

function Assert-TrustedLoopbackMcpProcess {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$BaseUrl,
        [Parameter(Mandatory)][string]$ExpectedScript
    )

    $base = [Uri]$BaseUrl
    if (-not $base.IsLoopback) { return }
    if (-not $IsWindows) {
        throw 'Credential-bearing loopback MCP smoke requires a Windows process attestation implementation.'
    }

    $expectedScriptFull = [IO.Path]::GetFullPath($ExpectedScript)
    $expectedPython = Resolve-TrustedApplication -Name 'python'
    $listeners = @(Get-NetTCPConnection -State Listen -LocalPort $base.Port -ErrorAction Stop |
        Where-Object { $_.LocalAddress -in @('127.0.0.1', '::1') })
    $processIds = @($listeners | Select-Object -ExpandProperty OwningProcess -Unique)
    if ($processIds.Count -ne 1) {
        throw 'Loopback MCP smoke requires exactly one attested listener process.'
    }
    $process = Get-CimInstance Win32_Process -Filter "ProcessId=$($processIds[0])" -ErrorAction Stop
    if (-not $process -or -not [string]::Equals(
        [IO.Path]::GetFullPath([string]$process.ExecutablePath),
        $expectedPython,
        [StringComparison]::OrdinalIgnoreCase
    )) {
        throw 'Loopback MCP listener is not running under the trusted Python interpreter.'
    }
    if ([string]$process.CommandLine -notmatch [regex]::Escape($expectedScriptFull)) {
        throw 'Loopback MCP listener is not the expected Echo OAuth connector process.'
    }
}

function Get-ApprovedPackageFiles {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$PluginRoot,
        [Parameter(Mandatory)][string]$AllowlistPath
    )

    if (-not (Test-Path -LiteralPath $AllowlistPath -PathType Leaf)) {
        throw "Package allowlist is missing: $AllowlistPath"
    }
    $approvedNames = [Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
    $selected = [Collections.Generic.List[object]]::new()
    foreach ($rawLine in Get-Content -LiteralPath $AllowlistPath) {
        $line = $rawLine.Trim()
        if (-not $line -or $line.StartsWith('#')) { continue }
        $optional = $line.StartsWith('?')
        $relative = if ($optional) { $line.Substring(1).Trim() } else { $line }
        if (
            -not $relative -or
            $relative.Contains('\') -or
            [IO.Path]::IsPathRooted($relative) -or
            $relative.Split('/') -contains '..'
        ) {
            throw "Invalid package allowlist entry: $rawLine"
        }
        if (-not $approvedNames.Add($relative)) {
            throw "Duplicate package allowlist entry: $relative"
        }
        $candidate = Assert-PathUnderRoot -Root $PluginRoot -Candidate (Join-Path $PluginRoot ($relative.Replace('/', [IO.Path]::DirectorySeparatorChar)))
        if (Test-Path -LiteralPath $candidate -PathType Leaf) {
            $selected.Add([pscustomobject]@{ Relative = $relative; FullName = $candidate })
        } elseif (-not $optional) {
            throw "Required package file is missing: $relative"
        }
    }

    $present = Get-ChildItem -LiteralPath $PluginRoot -Recurse -File -Force | ForEach-Object {
        [IO.Path]::GetRelativePath([IO.Path]::GetFullPath($PluginRoot), $_.FullName).Replace('\', '/')
    }
    $unexpected = @($present | Where-Object { -not $approvedNames.Contains($_) } | Sort-Object)
    if ($unexpected.Count -gt 0) {
        throw "Unexpected file in plugin source: $($unexpected -join ', ')"
    }
    return @($selected | Sort-Object Relative)
}
