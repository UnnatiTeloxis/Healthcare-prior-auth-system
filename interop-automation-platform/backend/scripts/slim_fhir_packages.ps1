$ErrorActionPreference = "Stop"
$pkgDir = "c:\Users\Admin\Healthcare-prior-auth-system-main\interop-automation-platform\backend\fhir_packages"
$work = Join-Path $env:TEMP "fhir-slim-pkgs"
if (Test-Path $work) { Remove-Item $work -Recurse -Force }
New-Item -ItemType Directory -Path $work | Out-Null

$files = @(
  "us-core.tgz",
  "davinci-hrex.tgz",
  "davinci-crd.tgz",
  "davinci-dtr.tgz",
  "davinci-pas.tgz"
)

foreach ($tgz in $files) {
  Write-Host "Slimming $tgz ..."
  $src = Join-Path $pkgDir $tgz
  $extract = Join-Path $work ($tgz.Replace(".tgz", ""))
  New-Item -ItemType Directory -Path $extract | Out-Null
  tar -xzf $src -C $extract

  $pkgJson = Get-ChildItem -Path $extract -Recurse -Filter "package.json" |
    Where-Object { $_.FullName -match "package[\\/]package\.json$" } |
    Select-Object -First 1

  if (-not $pkgJson) {
    $pkgJson = Get-ChildItem -Path $extract -Recurse -Filter "package.json" | Select-Object -First 1
  }
  if (-not $pkgJson) {
    Write-Host "  NO package.json"
    continue
  }

  $raw = Get-Content $pkgJson.FullName -Raw
  # Keep StructureDefinitions; clear dependencies so Inferno does not fetch packages.fhir.org
  $raw = [regex]::Replace($raw, '"dependencies"\s*:\s*\{[^}]*\}', '"dependencies" : {}', 1)
  if ($raw -notmatch '"dependencies"\s*:\s*\{\s*\}') {
    # multiline dependencies object
    $raw = [regex]::Replace(
      $raw,
      '"dependencies"\s*:\s*\{(?:[^{}]|\{[^{}]*\})*\}',
      '"dependencies" : {}',
      1
    )
  }
  $utf8NoBom = New-Object System.Text.UTF8Encoding $false
  [System.IO.File]::WriteAllText($pkgJson.FullName, $raw, $utf8NoBom)

  $out = Join-Path $pkgDir $tgz
  Push-Location $extract
  if (Test-Path ".\package") {
    tar -czf $out package
  } else {
    tar -czf $out *
  }
  Pop-Location
  Write-Host ("  wrote " + (Get-Item $out).Length + " bytes")
}

Write-Host "Done"
Get-ChildItem "$pkgDir\*.tgz" | Format-Table Name, Length
