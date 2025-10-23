# Experiments Test Suite (opt-in)

Purpose
- Give teammates a place to write quick pytest checks for code under `experiments/` without affecting CI.
- CI only runs tests under the top-level `tests/` directory. This folder is for local smoke/iteration.

How to run

PowerShell (Windows):
```
python -m pip install -r requirements.txt
python -m pytest -q -c experiments/pytest.ini
```

Bash (Linux/macOS):
```
python -m pip install -r requirements.txt
pytest -q -c experiments/pytest.ini
```

Notes
- These tests can import from `experiments.*` freely.
- Do NOT import from `experiments.*` in production tests under the top-level `tests/` directory.
- Keep these fast; they are for quick sanity checks while prototyping.
