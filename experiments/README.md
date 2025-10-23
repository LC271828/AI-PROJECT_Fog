# Experiments Sandbox

TL;DR (PowerShell from repo root)

```powershell
# Optional: install core deps (pytest). No runtime deps required yet.
python -m pip install -r requirements.txt

# Run the quickstart template (imports from src/ safely)
python experiments/_template/quickstart.py

# Make your own copy and run it
copy experiments/_template/quickstart.py experiments/leo/quickstart.py
python experiments/leo/quickstart.py
```

Purpose: give each teammate a safe playground for quick scripts, prototypes, and notebooks without touching production code.

Rules
- Do NOT import from `experiments/` in `src/` or `tests/`.
- Keep production code in `src/` and tests in `tests/`.
- If a prototype graduates, copy refined pieces into `src/` via a normal PR.
- Add any large data samples under a nested `data/` directory inside your folder and git-ignore as needed.

Structure
```
experiments/
  gibran/
  naufal/
  leo/
  thomz/
  bayu/
  asthar/
```

Suggested layout inside your folder
- `scratch.ipynb` or `scratch.py` for throwaway work
- `notes.md` for decisions
- `data/` for temporary inputs (consider updating `.gitignore` if large)

Examples
- See `experiments/_template/quickstart.py` for a tiny runner showing how to call production code safely.

## How to use quickstart

The quickstart shows how to import from `src/` while working under `experiments/`.

PowerShell (from repo root):

```powershell
# Optional: install dependencies if your experiment needs them
python -m pip install -r requirements.txt

# Run the quickstart template
python experiments/_template/quickstart.py

# Tip: copy it into your own sandbox and customize
copy experiments/_template/quickstart.py experiments/leo/quickstart.py
python experiments/leo/quickstart.py
```
