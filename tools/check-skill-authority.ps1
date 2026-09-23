$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path -Parent $scriptDir
$skillsSrc = Join-Path $repoRoot "skills"
$codexSkills = Join-Path $env:USERPROFILE ".codex\skills"
$agentsSkills = Join-Path $env:USERPROFILE ".agents\skills"
$failures = 0
$checked = 0

function Get-TreeDigest([string]$root) {
    $rootPath = (Resolve-Path $root).Path.TrimEnd('\')
    $lines = Get-ChildItem $rootPath -Recurse -File |
        Where-Object { $_.Name -ne ".DS_Store" } |
        Sort-Object FullName |
        ForEach-Object {
            $relative = $_.FullName.Substring($rootPath.Length).TrimStart('\')
            $hash = (Get-FileHash $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
            "$relative`t$hash"
        }
    $text = $lines -join "`n"
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($text)
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try {
        return ([System.BitConverter]::ToString($sha.ComputeHash($bytes))).Replace("-", "").ToLowerInvariant()
    } finally {
        $sha.Dispose()
    }
}

Get-ChildItem $skillsSrc -Directory | Where-Object { $_.Name -ne "skill-creator" } | ForEach-Object {
    $name = $_.Name
    $source = $_.FullName
    $deployed = Join-Path $codexSkills $name
    $duplicate = Join-Path $agentsSkills $name
    $script:checked++

    if (-not (Test-Path (Join-Path $deployed "SKILL.md"))) {
        Write-Host "MISSING`tCodex`t$name"
        $script:failures++
    } elseif ((Get-TreeDigest $source) -ne (Get-TreeDigest $deployed)) {
        Write-Host "DIFF`tCodex`t$name"
        $script:failures++
    } else {
        Write-Host "MATCH`tCodex`t$name"
    }

    if (Test-Path $duplicate) {
        Write-Host "DUPLICATE`tAgents`t$name"
        $script:failures++
    }
}

if (Test-Path (Join-Path $codexSkills "skill-creator")) {
    Write-Host "WARN`tCodex`tskill-creator 使用者副本存在；應停用並改用內建版"
    $failures++
}

if ($failures -gt 0) {
    throw "FAIL：檢查 $checked 個核心 Skill，發現 $failures 個來源問題。停止總控流程。"
}

Write-Host "PASS`t$checked 個核心 Skill 只由 repo 母版部署至 Codex；Claude／.agents 來源未參與。" -ForegroundColor Green
