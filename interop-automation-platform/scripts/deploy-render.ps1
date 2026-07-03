# Push and prepare Render Blueprint deploy.
# Usage: .\scripts\deploy-render.ps1

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

Write-Host "Preparing Render.com deployment..." -ForegroundColor Cyan

if (-not (Test-Path ".git")) {
    Write-Host "Not inside a git repository." -ForegroundColor Red
    exit 1
}

$Branch = if ($env:DEPLOY_BRANCH) { $env:DEPLOY_BRANCH } else { "interop-automation" }

$status = git status -s
if ($status) {
    Write-Host "Committing changes..." -ForegroundColor Yellow
    git add Dockerfile render.yaml .env.production .dockerignore `
        backend/fhir_packages backend/app/services/fhir_validator/fhir_loader.py `
        docs/DEPLOYMENT_RENDER.md README.md scripts/deploy-render.sh scripts/deploy-render.ps1 `
        ../render.yaml 2>$null
    git commit -m "Configure Render single-URL deployment"
}

Write-Host "Pushing to origin/$Branch..." -ForegroundColor Yellow
git push origin $Branch

Write-Host ""
Write-Host "Next: https://dashboard.render.com -> New + -> Blueprint" -ForegroundColor Green
Write-Host "  App:       https://interop-platform.onrender.com"
Write-Host "  Validator: https://interop-platform.onrender.com/fhir-validator.html"
