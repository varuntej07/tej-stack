[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [ValidateSet("codex", "claude", "both")]
    [string]$Target = "both",

    [ValidateSet("user", "project")]
    [string]$Scope = "user",

    [switch]$Update,

    [string]$HomeDirectory = [Environment]::GetFolderPath("UserProfile"),

    [string]$ProjectRoot = (Get-Location).Path
)

$ErrorActionPreference = "Stop"
$sourceDirectory = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot "..\skills\walkie-talkie"))
$sourceSkill = Join-Path $sourceDirectory "SKILL.md"

function Test-WalkieTalkieSkill {
    param([Parameter(Mandatory)][string]$SkillFile)
    if (-not (Test-Path -LiteralPath $SkillFile -PathType Leaf)) {
        return $false
    }
    $lines = @(Get-Content -LiteralPath $SkillFile)
    if ($lines.Count -lt 3 -or $lines[0] -ne '---') {
        return $false
    }
    $nameCount = 0
    for ($index = 1; $index -lt $lines.Count; $index++) {
        if ($lines[$index] -eq '---') {
            return $nameCount -eq 1
        }
        if ($lines[$index] -match '^name:\s*') {
            if ($lines[$index] -ne 'name: walkie-talkie') {
                return $false
            }
            $nameCount++
        }
    }
    return $false
}

if (-not (Test-WalkieTalkieSkill -SkillFile $sourceSkill)) {
    throw "The bundled walkie-talkie skill is missing or invalid."
}
if ($Scope -eq "user" -and [string]::IsNullOrWhiteSpace($HomeDirectory)) {
    throw "No user home directory is available."
}

function Get-Destination {
    param([Parameter(Mandatory)][ValidateSet("codex", "claude")][string]$Agent)
    $base = if ($Scope -eq "user") { $HomeDirectory } else { $ProjectRoot }
    $relative = if ($Agent -eq "codex") {
        ".agents\skills\walkie-talkie"
    } else {
        ".claude\skills\walkie-talkie"
    }
    return [IO.Path]::GetFullPath((Join-Path $base $relative))
}

function Test-Destination {
    param([Parameter(Mandatory)][string]$Destination)
    if (-not (Test-Path -LiteralPath $Destination)) {
        return
    }
    $installedSkill = Join-Path $Destination "SKILL.md"
    if (-not (Test-WalkieTalkieSkill -SkillFile $installedSkill)) {
        throw "Refusing to overwrite a different installation at: $Destination"
    }
    if (-not $Update) {
        throw "walkie-talkie is already installed at: $Destination. Re-run with -Update to replace this same skill."
    }
}

function Install-One {
    param([Parameter(Mandatory)][ValidateSet("codex", "claude")][string]$Agent)
    $destination = Get-Destination -Agent $Agent
    $parent = Split-Path -Parent $destination
    [void](New-Item -ItemType Directory -Path $parent -Force)
    $stage = Join-Path $parent (".walkie-talkie.install." + [IO.Path]::GetRandomFileName())
    [void](New-Item -ItemType Directory -Path $stage)

    try {
        Get-ChildItem -Force -LiteralPath $sourceDirectory | Copy-Item -Destination $stage -Recurse -Force
        if (Test-Path -LiteralPath $destination) {
            $backup = Join-Path $parent (".walkie-talkie.backup." + [IO.Path]::GetRandomFileName())
            Move-Item -LiteralPath $destination -Destination $backup
            try {
                Move-Item -LiteralPath $stage -Destination $destination
                Remove-Item -LiteralPath $backup -Recurse -Force
            } catch {
                if (-not (Test-Path -LiteralPath $destination) -and (Test-Path -LiteralPath $backup)) {
                    Move-Item -LiteralPath $backup -Destination $destination
                }
                throw
            }
        } else {
            Move-Item -LiteralPath $stage -Destination $destination
        }
    } finally {
        if (Test-Path -LiteralPath $stage) {
            Remove-Item -LiteralPath $stage -Recurse -Force
        }
    }

    $invocation = if ($Agent -eq "codex") { '$walkie-talkie' } else { '/walkie-talkie' }
    Write-Output "Installed walkie-talkie for $Agent at: $destination"
    Write-Output "Invoke it with: $invocation"
}

$agents = if ($Target -eq "both") { @("codex", "claude") } else { @($Target) }
foreach ($agent in $agents) {
    Test-Destination -Destination (Get-Destination -Agent $agent)
}
foreach ($agent in $agents) {
    Install-One -Agent $agent
}
