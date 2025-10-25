param(
  [switch]$WithGUI
)

$ErrorActionPreference = "Stop"

# Determine root and venv paths
$RepoRoot = Split-Path -Parent $PSCommandPath
$RepoRoot = Split-Path -Parent $RepoRoot # go up from scripts/
$VenvPath = Join-Path $RepoRoot ".venv"
$PythonExe = "python"

Write-Host "[setup] Repository: $RepoRoot" -ForegroundColor Cyan

# Create venv if missing
if (-not (Test-Path $VenvPath)) {
  Write-Host "[setup] Creating virtual environment at $VenvPath" -ForegroundColor Yellow
  & $PythonExe -m venv $VenvPath
}

# Resolve venv python
$VenvPython = Join-Path $VenvPath "Scripts/python.exe"
if (-not (Test-Path $VenvPython)) {
  throw "Could not find venv python at $VenvPython"
}

# Upgrade pip
& $VenvPython -m pip install --upgrade pip

# Install dependencies from requirements.txt when available (preferred),
# else fall back to installing pytest only. Optionally add pygame.
$req = Join-Path $RepoRoot "requirements.txt"
if (Test-Path $req) {
  Write-Host "[setup] Installing requirements.txt" -ForegroundColor Yellow
  & $VenvPython -m pip install -r $req
} else {
  Write-Host "[setup] requirements.txt not found; installing pytest only" -ForegroundColor Yellow
  & $VenvPython -m pip install pytest
}

if ($WithGUI) {
  Write-Host "[setup] Installing pygame (GUI)" -ForegroundColor Yellow
  & $VenvPython -m pip install pygame
}

Write-Host "[setup] Done. To use the venv in this shell, run:" -ForegroundColor Green
Write-Host ".\\.venv\\Scripts\\Activate.ps1" -ForegroundColor Green
