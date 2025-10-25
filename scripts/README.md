# Scripts

TL;DR (Windows, from repo root)

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
powershell -ExecutionPolicy Bypass -File .\scripts\setup.ps1          # venv + core deps
powershell -ExecutionPolicy Bypass -File .\scripts\test.ps1           # run pytest (verbose + rich summary)
# Optional (GUI)
powershell -ExecutionPolicy Bypass -File .\scripts\setup.ps1 -WithGUI # add pygame (GUI work)
# Or install pygame directly (any platform):
python -m pip install pygame
```

TL;DR (Linux/macOS)

```bash
# Setup (creates .venv, installs requirements; set WITH_GUI=1 to add pygame)
./scripts/setup.sh
# or
WITH_GUI=1 ./scripts/setup.sh

# Run tests (verbose + rich summary)
./scripts/test.sh

# Optional: use PowerShell Core on Linux to run the same .ps1 helpers
# (requires 'pwsh' to be installed)
pwsh -File ./scripts/create_issues_from_config.ps1 -SkipExisting
```

This folder contains:
- Dev environment helpers
- A config-driven workflow for creating and maintaining GitHub Issues
- Note: Demo entry points have moved to `examples/`. The old `scripts/demo_*` wrappers have been removed.

## Files
- `setup.ps1` — Creates `.venv` and installs dependencies (optional `-WithGUI` adds pygame).
- `test.ps1` — Activates `.venv` (if present) and runs `pytest`.
- `pull.ps1` — Fetch, checkout `dev`, and fast-forward pull.
- `commit.ps1` — Stage, commit, and push current HEAD to remote `dev`.
- `create_issues_from_config.ps1` — Reads a JSON config and creates/updates issues idempotently.
- `issues.json` — Repository slug, labels to ensure exist, and the list of issues to create/update.
- `maze_gen.py` — Generate large maze CSVs (odd sizes recommended). Example:

```powershell
python scripts/maze_gen.py --width 101 --height 101 --braid 0.10 --seed 42 --out maps/maze_101x101_b10.csv
```

Flags:
- `--width/--height`: dimensions (will be coerced to odd numbers)
- `--braid`: fraction of dead-ends to convert into loops (0.0 = perfect maze; 0.1–0.2 adds interesting branches)
- `--seed`: RNG seed for reproducibility
- `--out`: output CSV path (defaults to maps/maze_<WxH>_bXX.csv)

Notes for Linux users
- You don’t need the Windows PowerShell scripts; use `setup.sh` and `test.sh` above.
- If you prefer PowerShell, install PowerShell Core (`pwsh`) and invoke `.ps1` files with `pwsh -File`.
- For pygame on Linux, you may need system packages (SDL libraries) depending on your distro. If GUI work isn’t needed, skip it.

## Dev environment (PowerShell)

From the repo root on Windows:

```powershell
# Create a virtual environment and install base dev deps (pytest)
powershell -ExecutionPolicy Bypass -File .\scripts\setup.ps1

# Include GUI dependency (pygame) if you plan to work on visualization
powershell -ExecutionPolicy Bypass -File .\scripts\setup.ps1 -WithGUI

# Run tests (uses .venv if present, respects pytest.ini for verbose output + rich summary)
powershell -ExecutionPolicy Bypass -File .\scripts\test.ps1
```

## Simple Git helpers (PowerShell)

```powershell
# Pull latest changes into local 'dev'
powershell -ExecutionPolicy Bypass -File .\scripts\pull.ps1

# Commit all changes and push current HEAD to remote 'dev'
powershell -ExecutionPolicy Bypass -File .\scripts\commit.ps1 -Message "your message"
```

## Issue automation (PowerShell)

From the repo root on Windows:

```powershell
# One-time (per session)
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# Create/update issues defined in scripts/issues.json
powershell -ExecutionPolicy Bypass -File .\scripts\create_issues_from_config.ps1 -SkipExisting
```

Notes:
- `-SkipExisting` updates labels/assignees/comments of existing issues (matched by title)
  instead of creating duplicates. Re-run safely any time.
- If assignees haven’t accepted invitations yet, the script will auto-assign the
  fallback assignee from `issues.json` (currently `LC271828`).
- Bodies are piped via STDIN to avoid quoting issues.

## Test output (pretty summary)
- We enable per-test live logging and a Rich-based summary by default.
- To disable the summary, run: `python -m pytest -p no:tests.pytest_rich_report`.
- If your terminal has trouble rendering the panel, the plugin gracefully degrades when Rich is not available.

## Customizing
- Edit `scripts/issues.json` to change or add issues. Each item can include:
  - `title` (string)
  - `body` (string) or `bodyFile` (path to a .md file)
  - `labels` (array of label names)
  - `assignees` (array of GitHub logins)
  - `comments` (array of comments to post after creation)
  - Optional: `milestone`, `project`
- Update `repo` and `fallbackAssignee` at the top of `issues.json` as needed.

## Why remove create_issues.ps1?
The previous script hardcoded the issue set and could easily create duplicates on rerun.
The new config-driven script is idempotent and easier to maintain.

## Team handles mapping
Use these GitHub usernames in `issues.json` (and anywhere you assign reviewers):

- Leo Carter → `LC271828`
- Asthar → `Raffolklore`
- Muhammad Gibran Basyir → `cliverosf1eld`
- M. Ahsan Wiryawan → `Shazaw`
- Thomz → `Troggz`
- Bayu Putra Ibana → `hush1a`

Notes:
- If a collaborator hasn’t accepted the invite, assignment will fall back to `LC271828`.
- After they accept, rerun:
  - `powershell -ExecutionPolicy Bypass -File .\scripts\create_issues_from_config.ps1 -SkipExisting`
  to update assignees/labels/comments without creating duplicates.
