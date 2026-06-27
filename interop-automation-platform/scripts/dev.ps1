# Interop Automation Platform - Windows PowerShell helpers
# Usage: .\scripts\dev.ps1 build
#        .\scripts\dev.ps1 up
#        .\scripts\dev.ps1 start   (build + up)

param(
    [Parameter(Position = 0)]
    [ValidateSet("build", "up", "down", "logs", "start", "restart", "clean", "help")]
    [string]$Command = "help"
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

function Get-Compose {
    if (Get-Command docker -ErrorAction SilentlyContinue) {
        docker compose version 2>$null | Out-Null
        if ($LASTEXITCODE -eq 0) { return "docker compose" }
    }
    if (Get-Command docker-compose -ErrorAction SilentlyContinue) {
        return "docker-compose"
    }
    throw "Docker Compose not found. Install Docker Desktop and ensure it is running."
}

function Ensure-Env {
    if (-not (Test-Path ".env")) {
        Write-Host "Creating .env from .env.example..."
        Copy-Item ".env.example" ".env"
    }
}

switch ($Command) {
    "help" {
        Write-Host @"
Available commands (run from interop-automation-platform folder):

  .\scripts\dev.ps1 build     Build Docker images
  .\scripts\dev.ps1 up        Start all services
  .\scripts\dev.ps1 start     Build and start (recommended first run)
  .\scripts\dev.ps1 down      Stop services
  .\scripts\dev.ps1 logs      Follow logs
  .\scripts\dev.ps1 restart   Restart services
  .\scripts\dev.ps1 clean     Stop and remove volumes

Frontend only (local, no Docker):
  cd frontend
  npm install
  npm run dev

Or from project root:
  npm run build          # builds frontend
  npm run start          # docker compose up -d --build
"@
    }
    "build" {
        Ensure-Env
        $compose = Get-Compose
        Invoke-Expression "$compose build"
    }
    "up" {
        Ensure-Env
        $compose = Get-Compose
        Invoke-Expression "$compose up -d"
        Write-Host "Backend:  http://localhost:8000"
        Write-Host "Frontend: http://localhost:3000"
        Write-Host "API Docs: http://localhost:8000/docs"
    }
    "start" {
        Ensure-Env
        $compose = Get-Compose
        Invoke-Expression "$compose up -d --build"
        Write-Host "Backend:  http://localhost:8000"
        Write-Host "Frontend: http://localhost:3000"
    }
    "down" {
        $compose = Get-Compose
        Invoke-Expression "$compose down"
    }
    "logs" {
        $compose = Get-Compose
        Invoke-Expression "$compose logs -f"
    }
    "restart" {
        & $PSScriptRoot\dev.ps1 down
        & $PSScriptRoot\dev.ps1 up
    }
    "clean" {
        $compose = Get-Compose
        Invoke-Expression "$compose down -v"
    }
}
