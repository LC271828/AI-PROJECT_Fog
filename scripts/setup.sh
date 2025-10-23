#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   ./scripts/setup.sh            # venv + core deps from requirements.txt
#   WITH_GUI=1 ./scripts/setup.sh # also installs pygame

VENV_DIR=".venv"
PY="${PYTHON:-python3}"

if [ ! -d "$VENV_DIR" ]; then
  echo "[setup] Creating virtual environment at $VENV_DIR"
  "$PY" -m venv "$VENV_DIR"
fi

VENV_PY="$VENV_DIR/bin/python"
if [ ! -x "$VENV_PY" ]; then
  echo "Error: venv python not found at $VENV_PY" >&2
  exit 1
fi

"$VENV_PY" -m pip install --upgrade pip

# Install core deps
if [ -f requirements.txt ]; then
  echo "[setup] Installing requirements.txt"
  "$VENV_PY" -m pip install -r requirements.txt
else
  echo "[setup] requirements.txt not found; installing pytest only"
  "$VENV_PY" -m pip install pytest
fi

# Optional GUI dep
if [ "${WITH_GUI:-0}" = "1" ]; then
  echo "[setup] Installing pygame (GUI)"
  "$VENV_PY" -m pip install pygame
fi

echo "[setup] Done. Activate with: source .venv/bin/activate"