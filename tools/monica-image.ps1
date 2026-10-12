[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$Prompt,

    [ValidateSet("flux", "dalle", "sd", "playground", "ideogram")]
    [string]$Provider = "flux",

    [string]$Model,

    [ValidateSet("1024x1024", "768x1344", "1344x768", "1024x1792", "1792x1024")]
    [string]$Size = "1024x1024",

    [ValidateRange(1, 4)]
    [int]$Count = 1,

    [string]$AspectRatio = "ASPECT_1_1",

    [string]$OutputDirectory = "tmp/monica/images"
)

function Get-MonicaApiKey {
    $key = [Environment]::GetEnvironmentVariable("MONICA_API_KEY", "Process")
    if ([string]::IsNullOrWhiteSpace($key)) {
        $key = [Environment]::GetEnvironmentVariable("MONICA_API_KEY", "User")
    }
    if ([string]::IsNullOrWhiteSpace($key)) {
        throw "MONICA_API_KEY is missing. Run tools/setup-monica.ps1, then reopen PowerShell."
    }
    return $key
}

$defaults = @{
    flux       = "flux_dev"
    dalle      = "dall-e-3"
    sd         = "sdxl"
    playground = "playground-v2-5"
    ideogram   = "V_2"
}

if ([string]::IsNullOrWhiteSpace($Model)) {
    $Model = $defaults[$Provider]
}

$endpoint = ""
$payload = @{ prompt = $Prompt; model = $Model }
switch ($Provider) {
    "flux" {
        $endpoint = "/v1/image/gen/flux"
        $payload.size = $Size
        if ($Model -ne "flux_pro") { $payload.num_outputs = $Count }
    }
    "dalle" {
        $endpoint = "/v1/image/gen/dalle"
        if ($Count -ne 1) { throw "Monica DALL-E 3 API supports Count = 1 only." }
        $payload.size = $Size
        $payload.n = 1
        $payload.quality = "standard"
    }
    "sd" {
        $endpoint = "/v1/image/gen/sd"
        $payload.size = $Size
        if ($Model -eq "sdxl") { $payload.num_outputs = $Count }
        elseif ($Count -ne 1) { throw "Monica sd3 and sd3_5 support Count = 1 only." }
    }
    "playground" {
        $endpoint = "/v1/image/gen/playground"
        $payload.size = $Size
        $payload.count = $Count
    }
    "ideogram" {
        $endpoint = "/v1/image/gen/ideogram"
        if ($Count -ne 1) { throw "The Ideogram endpoint supports Count = 1 only." }
        $payload.aspect_ratio = $AspectRatio
    }
}

$headers = @{ Authorization = "Bearer $(Get-MonicaApiKey)"; "Content-Type" = "application/json" }
$body = $payload | ConvertTo-Json -Depth 6

try {
    $response = Invoke-RestMethod `
        -Uri "https://openapi.monica.im$endpoint" `
        -Method Post `
        -Headers $headers `
        -Body $body `
        -TimeoutSec 180
} catch {
    $detail = $_.ErrorDetails.Message
    if ([string]::IsNullOrWhiteSpace($detail)) { $detail = $_.Exception.Message }
    throw "Monica image generation failed: $detail"
}

$urls = @($response.data | ForEach-Object {
    if ($_ -is [string]) { $_ } elseif ($null -ne $_.url) { $_.url }
}) | Where-Object { -not [string]::IsNullOrWhiteSpace($_) }
if ($urls.Count -eq 0) {
    throw "Monica did not return image URLs. Response: $($response | ConvertTo-Json -Depth 10 -Compress)"
}

$targetDirectory = Join-Path (Get-Location) $OutputDirectory
New-Item -ItemType Directory -Force -Path $targetDirectory | Out-Null
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$results = foreach ($url in $urls) {
    $index = [array]::IndexOf($urls, $url) + 1
    $file = Join-Path $targetDirectory "monica-$Provider-$timestamp-$index.png"
    Invoke-WebRequest -Uri $url -OutFile $file
    [pscustomobject]@{ provider = $Provider; model = $Model; prompt = $Prompt; source_url = $url; file = $file }
}

$results | ConvertTo-Json -Depth 5
