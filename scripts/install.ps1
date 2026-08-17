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
$sourceDirectory = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot "..\plugins\tej-stack\skills"))
$skills = @(Get-ChildItem -LiteralPath $sourceDirectory -Directory | Where-Object {
    Test-Path -LiteralPath (Join-Path $_.FullName "SKILL.md") -PathType Leaf
} | Sort-Object Name)

if ($skills.Count -eq 0) {
    throw "No bundled skills found."
}
if ($Scope -eq "user" -and [string]::IsNullOrWhiteSpace($HomeDirectory)) {
    throw "No user home directory is available."
}

function Test-ExpectedSkill {
    param(
        [Parameter(Mandatory)][string]$SkillFile,
        [Parameter(Mandatory)][string]$ExpectedName
    )
    if (-not (Test-Path -LiteralPath $SkillFile -PathType Leaf)) {
        return $false
    }
    $lines = @(Get-Content -LiteralPath $SkillFile)
    if ($lines.Count -lt 3 -or $lines[0] -ne "---") {
        return $false
    }
    $nameCount = 0
    for ($index = 1; $index -lt $lines.Count; $index++) {
        if ($lines[$index] -eq "---") {
            return $nameCount -eq 1
        }
        if ($lines[$index] -match "^name:\s*") {
            if ($lines[$index] -ne "name: $ExpectedName") {
                return $false
            }
            $nameCount++
        }
    }
    return $false
}

function Get-Destination {
    param(
        [Parameter(Mandatory)][ValidateSet("codex", "claude")][string]$Agent,
        [Parameter(Mandatory)][string]$SkillName
    )
    if ($Scope -eq "user") {
        $relative = if ($Agent -eq "codex") {
            ".codex\skills\$SkillName"
        } else {
            ".claude\skills\$SkillName"
        }
        return [IO.Path]::GetFullPath((Join-Path $HomeDirectory $relative))
    }
    $relative = if ($Agent -eq "codex") {
        ".agents\skills\$SkillName"
    } else {
        ".claude\skills\$SkillName"
    }
    return [IO.Path]::GetFullPath((Join-Path $ProjectRoot $relative))
}

function Test-Destination {
    param(
        [Parameter(Mandatory)][string]$Agent,
        [Parameter(Mandatory)][System.IO.DirectoryInfo]$Skill
    )
    $sourceSkill = Join-Path $Skill.FullName "SKILL.md"
    if (-not (Test-ExpectedSkill -SkillFile $sourceSkill -ExpectedName $Skill.Name)) {
        throw "Bundled skill is missing or invalid: $($Skill.Name)"
    }
    $destination = Get-Destination -Agent $Agent -SkillName $Skill.Name
    if (-not (Test-Path -LiteralPath $destination)) {
        return
    }
    if (-not (Test-ExpectedSkill -SkillFile (Join-Path $destination "SKILL.md") -ExpectedName $Skill.Name)) {
        throw "Refusing to overwrite a different installation at: $destination"
    }
    if (-not $Update) {
        throw "$($Skill.Name) is already installed at: $destination. Re-run with -Update to replace this same skill."
    }
}

function Install-One {
    param(
        [Parameter(Mandatory)][string]$Agent,
        [Parameter(Mandatory)][System.IO.DirectoryInfo]$Skill
    )
    $destination = Get-Destination -Agent $Agent -SkillName $Skill.Name
    $parent = Split-Path -Parent $destination
    [void](New-Item -ItemType Directory -Path $parent -Force)
    $stage = Join-Path $parent (".tej-stack.install." + [IO.Path]::GetRandomFileName())
    [void](New-Item -ItemType Directory -Path $stage)

    try {
        Get-ChildItem -Force -LiteralPath $Skill.FullName | Copy-Item -Destination $stage -Recurse -Force
        if (Test-Path -LiteralPath $destination) {
            $backup = Join-Path $parent (".tej-stack.backup." + [IO.Path]::GetRandomFileName())
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

    $invocation = if ($Agent -eq "codex") { '$' + $Skill.Name } else { '/' + $Skill.Name }
    Write-Output "Installed $($Skill.Name) for $Agent at: $destination"
    Write-Output "Invoke it with: $invocation"
}

$agents = if ($Target -eq "both") { @("codex", "claude") } else { @($Target) }
foreach ($agent in $agents) {
    foreach ($skill in $skills) {
        Test-Destination -Agent $agent -Skill $skill
    }
}
foreach ($agent in $agents) {
    foreach ($skill in $skills) {
        Install-One -Agent $agent -Skill $skill
    }
}
