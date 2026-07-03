# Push deployment configuration to GitHub and trigger Render Blueprint deploy.
# Usage (from interop-automation-platform/):
#   .\scripts\deploy-render.ps1

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

Write-Host "Starting Render.com deployment prep..." -ForegroundColor Cyan

if (-not (Test-Path ".git")) {
    Write-Host "Not inside a git repository. Initialize git and connect GitHub first." -ForegroundColor Red
    exit 1
}

$remote = git remote get-url origin 2>$null
if (-not $remote) {
    Write-Host "No GitHub remote 'origin' configured." -ForegroundColor Red
    exit 1
}

$Branch = if ($env:DEPLOY_BRANCH) { $env:DEPLOY_BRANCH } else { "main" }

$status = git status -s
if ($status) {
    Write-Host "Committing deployment configuration..." -ForegroundColor Yellow
    git add render.yaml backend/Dockerfile.render backend/render.yaml `
        frontend/Dockerfile.render frontend/nginx.render.conf `
        docker-compose.render.yml .env.production .dockerignore `
        scripts/deploy-render.sh scripts/deploy-render.ps1 `
        docs/DEPLOYMENT_RENDER.md README.md 2>$null
    git commit -m "Add Render.com deployment configuration"
}

Write-Host "Pushing to GitHub (branch: $Branch)..." -ForegroundColor Yellow
git push origin $Branch

Write-Host ""
Write-Host "Deployment push complete." -ForegroundColor Green
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Open https://dashboard.render.com"
Write-Host "  2. New + -> Blueprint -> connect your repository"
Write-Host "  3. Select render.yaml (repo root or interop-automation-platform/)"
Write-Host "  4. Set INFERNO_VALIDATOR_URL in the backend service environment"
Write-Host "  5. Apply and wait 5-10 minutes"
Write-Host ""
Write-Host "Expected URLs:" -ForegroundColor Cyan
Write-Host "  Backend:  https://fhir-validator-backend.onrender.com"
Write-Host "  Frontend: https://fhir-validator-frontend.onrender.com"
Write-Host "  Health:   https://fhir-validator-backend.onrender.com/health"
