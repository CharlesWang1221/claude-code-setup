[CmdletBinding()]
param(
    [switch]$CheckOnly,
    [switch]$CleanLegacy,
    [switch]$ResetMemory,
    [string[]]$MemoryWorkspace,
    [string]$ProjectBundle,
    [string]$ProjectDirectory,
    [switch]$SkipCodex
)
$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
$workspaceRoot = Split-Path -Parent $repoRoot
if (-not $ProjectDirectory) {
    $ProjectDirectory = Join-Path $workspaceRoot "projects\liaoyu"
}
if ($CheckOnly -and ($CleanLegacy -or $ResetMemory -or $ProjectBundle)) {
    throw "CheckOnly cannot clean, reset memory, or import a project."
}

$pythonExe = $null
$pythonPrefix = @()
foreach ($candidate in @("py", "python3", "python")) {
    $command = Get-Command $candidate -ErrorAction SilentlyContinue
    if (-not $command) { continue }
    $prefix = @()
    if ($candidate -eq "py") { $prefix = @("-3") }
    & $command.Source @prefix -c "import sys; sys.exit(0 if sys.version_info >= (3,9) else 1)" 2>$null
    if ($LASTEXITCODE -eq 0) {
        $pythonExe = $command.Source
        $pythonPrefix = $prefix
        break
    }
}
if (-not $pythonExe) { throw "Python 3.9+ is required. Install Python before syncing." }

if (-not $SkipCodex) {
    if ($CheckOnly) {
        & (Join-Path $PSScriptRoot "check-skill-authority.ps1")
    } else {
        & (Join-Path $PSScriptRoot "sync-codex.ps1")
    }
}

$syncArgs = @((Join-Path $PSScriptRoot "sync-claude.py"), "--global-rules")
if (-not $CheckOnly) { $syncArgs += "--apply" }
if ($CleanLegacy) { $syncArgs += "--clean-legacy" }
if ($ResetMemory) {
    if (-not $MemoryWorkspace) { $MemoryWorkspace = @($repoRoot, $workspaceRoot) }
    foreach ($workspace in $MemoryWorkspace) {
        $syncArgs += @("--reset-memory", $workspace)
    }
}
& $pythonExe @pythonPrefix @syncArgs
if ($LASTEXITCODE -ne 0) { throw "Claude sync failed. See the audit output." }

if ($ProjectBundle) {
    & $pythonExe @pythonPrefix (Join-Path $PSScriptRoot "import-private-project.py") `
        $ProjectBundle --destination $ProjectDirectory
    if ($LASTEXITCODE -ne 0) { throw "Private project import failed." }
}
Write-Host "PASS: shared rules and core Skills verified. MCP credentials were not copied."
Write-Host "Open a NEW Codex/Claude Code session after syncing."
if ($ProjectBundle) { Write-Host "Project entry: $ProjectDirectory\HANDOFF.md" }
