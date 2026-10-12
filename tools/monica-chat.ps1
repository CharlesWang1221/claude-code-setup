[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$Prompt,

    [string]$Model = "gpt-4o",

    [switch]$Json
)

$apiKey = [Environment]::GetEnvironmentVariable("MONICA_API_KEY", "Process")
if ([string]::IsNullOrWhiteSpace($apiKey)) {
    $apiKey = [Environment]::GetEnvironmentVariable("MONICA_API_KEY", "User")
}

if ([string]::IsNullOrWhiteSpace($apiKey)) {
    throw "MONICA_API_KEY is missing. Run tools/setup-monica.ps1, then reopen PowerShell."
}

$requestBody = @{
    model = $Model
    messages = @(
        @{
            role = "user"
            content = @(
                @{
                    type = "text"
                    text = $Prompt
                }
            )
        }
    )
} | ConvertTo-Json -Depth 8

$headers = @{
    Authorization = "Bearer $apiKey"
    "Content-Type" = "application/json"
}

try {
    $response = Invoke-RestMethod `
        -Uri "https://openapi.monica.im/v1/chat/completions" `
        -Method Post `
        -Headers $headers `
        -Body $requestBody `
        -TimeoutSec 120
} catch {
    $detail = $_.ErrorDetails.Message
    if ([string]::IsNullOrWhiteSpace($detail)) {
        $detail = $_.Exception.Message
    }
    throw "Monica API request failed: $detail"
}

if ($Json) {
    $response | ConvertTo-Json -Depth 16
    return
}

$text = $response.choices[0].message.content
if ($text -is [System.Array]) {
    $text = ($text | ForEach-Object { $_.text }) -join ""
}

if ([string]::IsNullOrWhiteSpace($text)) {
    throw "Monica API did not return readable text. Re-run with -Json to inspect the response."
}

$text
