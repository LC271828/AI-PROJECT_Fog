param(
  [string]$Message = "work in progress"
)

$ErrorActionPreference = "Stop"

Write-Host "[commit] Staging changes..." -ForegroundColor Cyan
& git add .

try {
  Write-Host "[commit] Committing..." -ForegroundColor Cyan
  & git commit -m $Message
} catch {
  Write-Host "[commit] Nothing to commit (working tree clean)" -ForegroundColor Yellow
}

Write-Host "[commit] Pushing current HEAD to remote 'dev'..." -ForegroundColor Cyan
& git push origin HEAD:dev

Write-Host "[commit] Done." -ForegroundColor Green
