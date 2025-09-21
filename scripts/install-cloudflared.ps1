# Downloads cloudflared.exe into tools/ for local use without winget/choco
$ErrorActionPreference = 'Stop'

$tools = Join-Path (Split-Path -Parent $PSScriptRoot) 'tools'
New-Item -ItemType Directory -Force -Path $tools | Out-Null

# Choose latest Windows amd64 release from Cloudflare
$zipUrl = 'https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe'
$exePath = Join-Path $tools 'cloudflared.exe'

Write-Host "Downloading cloudflared..." -ForegroundColor Cyan
Invoke-WebRequest -Uri $zipUrl -OutFile $exePath

if (-not (Test-Path $exePath)) {
    Write-Error 'Download failed.'
    exit 1
}

Write-Host "cloudflared downloaded to: $exePath" -ForegroundColor Green
Write-Host "You can now run: .\\scripts\\tunnel.ps1" -ForegroundColor Green