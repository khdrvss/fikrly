# Opens a Cloudflare tunnel to your local Django dev server
# - Quick Tunnel (default): generates a trycloudflare.com URL
# - Managed Tunnel (Zero Trust): provide -Token (from Dashboard) to use your *.cfargotunnel.com hostname
param(
    [int]$Port = 8000,
    [string]$Token,
    [switch]$NoAutoUpdate
)

$ErrorActionPreference = 'Stop'

# Resolve cloudflared path (PATH or local tools folder)
$cloudflaredCmd = Get-Command cloudflared -ErrorAction SilentlyContinue
if (-not $cloudflaredCmd) {
    $localExe = Join-Path (Split-Path -Parent $PSScriptRoot) 'tools/cloudflared.exe'
    if (Test-Path $localExe) {
        $cloudflaredCmd = $localExe
    } else {
        Write-Host "cloudflared not found on PATH and no local copy at 'tools/cloudflared.exe'." -ForegroundColor Yellow
        Write-Host "Run the helper to download it:" -ForegroundColor Yellow
        Write-Host "  .\\scripts\\install-cloudflared.ps1" -ForegroundColor Yellow
        Write-Host "Or install via package manager (one of):" -ForegroundColor Yellow
        Write-Host "  winget install --id Cloudflare.CloudflareTunnel --exact --accept-package-agreements --accept-source-agreements" -ForegroundColor Yellow
        Write-Host "  choco install cloudflared -y" -ForegroundColor Yellow
        exit 1
    }
}

# Compose base args
$argsList = @()
if ($NoAutoUpdate) {
    $argsList += '--no-autoupdate'
} else {
    # Disable autoupdate by default to avoid permission issues in repo tools folder
    $argsList += '--no-autoupdate'
}

if ($Token -and $Token.Trim() -ne '') {
    Write-Host "Starting managed tunnel with provided token..." -ForegroundColor Cyan
    # Remotely-managed tunnel: routing/hostnames must be configured in Zero Trust dashboard
    & $cloudflaredCmd tunnel @argsList run --token $Token
} else {
    Write-Host "Starting Quick Tunnel to http://127.0.0.1:$Port ..." -ForegroundColor Cyan
    & $cloudflaredCmd tunnel @argsList --url "http://127.0.0.1:$Port"
}