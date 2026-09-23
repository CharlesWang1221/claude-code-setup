$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path -Parent $scriptDir
$skillsSrc = Join-Path $repoRoot "skills"
$codexSkills = Join-Path $env:USERPROFILE ".codex\skills"
$globalRulesSrc = Join-Path $repoRoot "codex\AGENTS.global.md"
$codexHome = Join-Path $env:USERPROFILE ".codex"

Write-Host "=== 同步 Skills（repo → Codex）===" -ForegroundColor Cyan
New-Item -ItemType Directory -Force $codexSkills | Out-Null

Get-ChildItem $skillsSrc -Directory | ForEach-Object {
    if ($_.Name -eq "skill-creator") {
        Write-Host "  跳過 skill-creator：Codex 固定使用內建版" -ForegroundColor Gray
    } else {
        $destination = Join-Path $codexSkills $_.Name
        if (Test-Path $destination) {
            Remove-Item -Recurse -Force $destination
        }
        Copy-Item -Recurse -Force $_.FullName $destination
        Write-Host "  已同步：$($_.Name)" -ForegroundColor Green
    }
}

New-Item -ItemType Directory -Force $codexHome | Out-Null
Copy-Item -Force $globalRulesSrc (Join-Path $codexHome "AGENTS.md")
Write-Host "  已同步 Codex 全域規則" -ForegroundColor Green

& (Join-Path $scriptDir "isolate-legacy-skills.ps1")
& (Join-Path $scriptDir "check-skill-authority.ps1")

Write-Host "=== 完成：Claude Skills 與 Claude MCP 未讀取、未同步 ===" -ForegroundColor Green
Write-Host "請重新啟動 Codex，讓 Skill 清單重新探索。" -ForegroundColor Yellow
