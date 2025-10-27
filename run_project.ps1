# Run setup (with GUI dependencies)
powershell -ExecutionPolicy Bypass -File .\scripts\setup.ps1 -WithGUI

# Activate the virtual environment
. .\.venv\Scripts\Activate.ps1

# Run the main program
python -m src.main
