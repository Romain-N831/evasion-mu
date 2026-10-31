$ErrorActionPreference = "Stop"

$ProjectRoot = $PSScriptRoot
$BackendPath = Join-Path $ProjectRoot "backend"

Set-Location $BackendPath

python manage.py check

if ($LASTEXITCODE -ne 0) {
    throw "Django checks failed. Availability was not generated."
}

python manage.py generate_demo_availability `
    --activity-days 30 `
    --room-days 90 `
    --times "09:00,13:00,16:00"

if ($LASTEXITCODE -ne 0) {
    throw "Availability generation failed."
}