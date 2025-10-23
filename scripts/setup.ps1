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

# Install base test/runtime deps
$base = @("pytest")
if ($WithGUI) {
  $base += @("pygame")
}

Write-Host "[setup] Installing packages: $($base -join ', ')" -ForegroundColor Yellow
& $VenvPython -m pip install @base

Write-Host "[setup] Done. To use the venv in this shell, run:" -ForegroundColor Green
Write-Host ".\\.venv\\Scripts\\Activate.ps1" -ForegroundColor Green
