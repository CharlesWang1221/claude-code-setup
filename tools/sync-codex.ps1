$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path -Parent $scriptDir
$skillsSrc = Join-Path $repoRoot "skills"
# Codex 有設 CODEX_HOME 時從那裡讀 Skills、規則與角色（Windows 這台是 %LOCALAPPDATA%\CodexCLI），沒設才是 ~/.codex
$codexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $env:USERPROFILE ".codex" }
$codexSkills = Join-Path $codexHome "skills"
$globalRulesSrc = Join-Path $repoRoot "codex\AGENTS.global.md"
Write-Host "Codex 目錄：$codexHome"

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

# Codex 多代理角色（阿派、廠長、鐵雄、省長等；config.toml 與 MCP 憑證仍只留本機）
$codexAgentRolesSrc = Join-Path $repoRoot "codex\agents"
$codexAgentRolesDest = Join-Path $codexHome "agents"
if (Test-Path $codexAgentRolesSrc) {
    New-Item -ItemType Directory -Force $codexAgentRolesDest | Out-Null
    Copy-Item -Force (Join-Path $codexAgentRolesSrc "*.toml") $codexAgentRolesDest
    $agentRoleCount = (Get-ChildItem $codexAgentRolesSrc -Filter "*.toml" -File).Count
    Write-Host "  已同步 $agentRoleCount 個 Codex 多代理角色" -ForegroundColor Green
}

& (Join-Path $scriptDir "isolate-legacy-skills.ps1")
& (Join-Path $scriptDir "check-skill-authority.ps1")

Write-Host "=== 完成：Claude Skills 與 Claude MCP 未讀取、未同步 ===" -ForegroundColor Green
Write-Host "請重新啟動 Codex，讓 Skill 清單重新探索。" -ForegroundColor Yellow
