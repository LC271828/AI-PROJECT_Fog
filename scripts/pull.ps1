$ErrorActionPreference = "Stop"

Write-Host "[pull] Fetching..." -ForegroundColor Cyan
& git fetch --all --prune

Write-Host "[pull] Checking out 'dev'..." -ForegroundColor Cyan
& git checkout dev

Write-Host "[pull] Pulling latest changes (fast-forward if possible)..." -ForegroundColor Cyan
& git pull --ff-only

Write-Host "[pull] Done." -ForegroundColor Green
