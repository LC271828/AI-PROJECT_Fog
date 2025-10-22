# Scripts

This folder contains:
- Dev environment helpers
- A config-driven workflow for creating and maintaining GitHub Issues

## Files
- `create_issues_from_config.ps1` — Reads a JSON config and creates/updates issues idempotently.
- `issues.json` — Repository slug, labels to ensure exist, and the list of issues to create/update.

## Dev environment (PowerShell)

From the repo root on Windows:

```powershell
# Create a virtual environment and install base dev deps (pytest)
powershell -ExecutionPolicy Bypass -File .\scripts\setup.ps1

# Include GUI dependency (pygame) if you plan to work on visualization
powershell -ExecutionPolicy Bypass -File .\scripts\setup.ps1 -WithGUI

# Run tests (uses .venv if present)
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
- Muhammad Gibran Basyir → `cliverosfield`
- M. Ahsan Wiryawan → `Shazaw`
- Thomz → `Troggz`
- Bayu Putra Ibana → `hush1a`

Notes:
- If a collaborator hasn’t accepted the invite, assignment will fall back to `LC271828`.
- After they accept, rerun:
  - `powershell -ExecutionPolicy Bypass -File .\scripts\create_issues_from_config.ps1 -SkipExisting`
  to update assignees/labels/comments without creating duplicates.
