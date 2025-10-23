# Run pytest using the repo's virtual environment if present, else system Python

$RepoRoot = Split-Path -Parent $PSCommandPath
$RepoRoot = Split-Path -Parent $RepoRoot # up from scripts/
$VenvPython = Join-Path $RepoRoot ".venv/Scripts/python.exe"

if (Test-Path $VenvPython) {
  & $VenvPython -m pytest -q
} else {
  Write-Host "[test] No .venv found, using system Python" -ForegroundColor Yellow
  python -m pytest -q
}
