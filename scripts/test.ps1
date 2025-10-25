# Run pytest using the repo's virtual environment if present, else system Python

$RepoRoot = Split-Path -Parent $PSCommandPath
$RepoRoot = Split-Path -Parent $RepoRoot # up from scripts/
$VenvPython = Join-Path $RepoRoot ".venv/Scripts/python.exe"

if (Test-Path $VenvPython) {
  # Rely on pytest.ini for verbosity/logging; avoid overriding with -q
  & $VenvPython -m pytest
} else {
  Write-Host "[test] No .venv found, using system Python" -ForegroundColor Yellow
  python -m pytest
}
