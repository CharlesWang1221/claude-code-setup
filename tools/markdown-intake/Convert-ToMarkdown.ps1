[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [ValidateNotNullOrEmpty()]
    [string]$InputPath,

    [Parameter(Mandatory)]
    [ValidateNotNullOrEmpty()]
    [string]$OutputPath,

    [switch]$Force
)

$ErrorActionPreference = 'Stop'
$source = Get-Item -LiteralPath $InputPath

if ($source.PSIsContainer) {
    throw 'InputPath 必須是一個檔案，不可直接轉換資料夾。'
}

$targetDirectory = Split-Path -Parent $OutputPath
if ($targetDirectory) {
    New-Item -ItemType Directory -Force -Path $targetDirectory | Out-Null
}

if ((Test-Path -LiteralPath $OutputPath) -and -not $Force) {
    throw "輸出檔已存在：$OutputPath。確認要覆蓋時加上 -Force。"
}

$localPackages = Join-Path $PSScriptRoot '.packages'
if (Test-Path -LiteralPath (Join-Path $localPackages 'markitdown')) {
    $previousPythonPath = $env:PYTHONPATH
    try {
        $env:PYTHONPATH = if ($previousPythonPath) { "$localPackages;$previousPythonPath" } else { $localPackages }
        & py -m markitdown $source.FullName -o $OutputPath
        $conversionExitCode = $LASTEXITCODE
    }
    finally {
        $env:PYTHONPATH = $previousPythonPath
    }
}
else {
    & py -m markitdown $source.FullName -o $OutputPath
    $conversionExitCode = $LASTEXITCODE
}

if ($conversionExitCode -ne 0) {
    throw "MarkItDown 轉換失敗，結束碼：$conversionExitCode"
}

if (-not (Test-Path -LiteralPath $OutputPath)) {
    throw 'MarkItDown 沒有產生預期的輸出檔。'
}

Write-Host "已建立 Markdown：$OutputPath"
