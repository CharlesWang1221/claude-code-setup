$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path -Parent $scriptDir
$skillsSrc = Join-Path $repoRoot "skills"
$runStamp = Get-Date -Format "yyyyMMdd-HHmmss"
$agentsSkills = Join-Path $env:USERPROFILE ".agents\skills"
$agentsBackup = Join-Path $env:USERPROFILE ".agents\codex-disabled-skills\$runStamp"
$codexSkills = Join-Path $env:USERPROFILE ".codex\skills"
$codexBackup = Join-Path $env:USERPROFILE ".codex\codex-disabled-skills\$runStamp"

Get-ChildItem $skillsSrc -Directory | Where-Object { $_.Name -ne "skill-creator" } | ForEach-Object {
    $legacyPath = Join-Path $agentsSkills $_.Name
    if (Test-Path $legacyPath) {
        New-Item -ItemType Directory -Force $agentsBackup | Out-Null
        $backupPath = Join-Path $agentsBackup $_.Name
        Move-Item -Force $legacyPath $backupPath
        Write-Host "ISOLATED`tAgents`t$($_.Name)`t$backupPath"
    }
}

$userSkillCreator = Join-Path $codexSkills "skill-creator"
if (Test-Path $userSkillCreator) {
    New-Item -ItemType Directory -Force $codexBackup | Out-Null
    $backupPath = Join-Path $codexBackup "skill-creator"
    Move-Item -Force $userSkillCreator $backupPath
    Write-Host "ISOLATED`tCodex`tskill-creator`t$backupPath"
}
