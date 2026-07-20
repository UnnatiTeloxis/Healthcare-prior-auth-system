# Pre-download FHIR IG packages to local disk (default: D:\fhir_packages).
# Usage:
#   .\scripts\download-igs.ps1
#   .\scripts\download-igs.ps1 -Scope catalog
#   .\scripts\download-igs.ps1 -Output "D:\fhir_packages" -NoDeps

param(
    [ValidateSet("popular", "catalog")]
    [string]$Scope = "catalog",
    [string]$Output = "D:\fhir_packages",
    [switch]$NoDeps,
    [switch]$Verbose,
    [double]$Delay = 3
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Backend = Join-Path $Root "backend"

if (-not (Test-Path $Output)) {
    New-Item -ItemType Directory -Path $Output -Force | Out-Null
    Write-Host "Created $Output"
}

Set-Location $Backend

$argsList = @(
    "scripts/download_ig_packages.py",
    "--scope", $Scope,
    "--output", $Output,
    "--delay", $Delay
)
if ($NoDeps) { $argsList += "--no-deps" }
if ($Verbose) { $argsList += "-v" }

Write-Host "Downloading IGs (scope=$Scope) to $Output ..."
Write-Host "Catalog scope downloads all US R4 IGs (~158 packages). With dependencies this can take 1-3+ hours."
python @argsList
