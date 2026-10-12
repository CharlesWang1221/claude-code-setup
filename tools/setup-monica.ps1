[CmdletBinding()]
param()

$secure = Read-Host "Paste Monica API Key (input is hidden)" -AsSecureString
$ptr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
try {
    $key = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr)
} finally {
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr)
}

if ([string]::IsNullOrWhiteSpace($key)) {
    throw "No API key entered; setup cancelled."
}

[Environment]::SetEnvironmentVariable("MONICA_API_KEY", $key, "User")
$env:MONICA_API_KEY = $key
Write-Host "Monica API Key saved to the current Windows user environment." -ForegroundColor Green
Write-Host "Test with: .\tools\monica-chat.ps1 'Reply only: Monica connected.'" -ForegroundColor Cyan
