[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [ValidatePattern('^https://')]
    [string]$ImageUrl,

    [ValidateSet(2)]
    [int]$Scale = 2,

    [string]$OutputDirectory = "tmp/monica/upscaled"
)

$apiKey = [Environment]::GetEnvironmentVariable("MONICA_API_KEY", "Process")
if ([string]::IsNullOrWhiteSpace($apiKey)) {
    $apiKey = [Environment]::GetEnvironmentVariable("MONICA_API_KEY", "User")
}
if ([string]::IsNullOrWhiteSpace($apiKey)) {
    throw "MONICA_API_KEY is missing. Run tools/setup-monica.ps1, then reopen PowerShell."
}

$headers = @{ Authorization = "Bearer $apiKey"; "Content-Type" = "application/json" }
$body = @{ image = $ImageUrl; scale = $Scale } | ConvertTo-Json

try {
    $response = Invoke-RestMethod `
        -Uri "https://openapi.monica.im/v1/image/tool/upscale" `
        -Method Post `
        -Headers $headers `
        -Body $body `
        -TimeoutSec 180
} catch {
    $detail = $_.ErrorDetails.Message
    if ([string]::IsNullOrWhiteSpace($detail)) { $detail = $_.Exception.Message }
    throw "Monica image upscale failed: $detail"
}

if ([string]::IsNullOrWhiteSpace($response.image)) {
    throw "Monica did not return an upscaled image URL. Response: $($response | ConvertTo-Json -Depth 8 -Compress)"
}

$targetDirectory = Join-Path (Get-Location) $OutputDirectory
New-Item -ItemType Directory -Force -Path $targetDirectory | Out-Null
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$outputFile = Join-Path $targetDirectory "monica-upscale-$timestamp.png"
Invoke-WebRequest -Uri $response.image -OutFile $outputFile

[pscustomobject]@{
    input_url = $ImageUrl
    source_url = $response.image
    scale = $Scale
    file = $outputFile
} | ConvertTo-Json -Depth 5
