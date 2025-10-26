# Contributing

This repo is currently a scaffold with TODOs.

- Keep search algorithms pure (no pygame, no I/O)
- Tests first for new behaviors
- Small, focused PRs
- Add implementations incrementally and update tests/docs accordingly

## Experiments sandbox

Use `experiments/` for quick prototypes, notebooks, and ad-hoc scripts. Each teammate has a folder:

```
experiments/
	gibran/
	naufal/
	leo/
```

Rules:
- Do not import from `experiments/` inside `src/` or `tests/`.
- Treat code here as disposable; promote stable code into `src/` via PR.
- Large temporary data should live under `experiments/<you>/data/` (git-ignored by default).

## Branch workflow
- Default: work directly on `dev` (shared integration). Keep commits small and focused.
- For a specific bug/feature that's risky or larger, create a short-lived branch from `dev` and open a PR back into `dev`.
- Only the integrator (Leo) merges `dev` → `main`. The `main` branch is protected.

## Terminology and assumptions
- Movement is up/down/left/right only (no diagonals)
- Visibility is radius 1; walls are visible when adjacent and block reveal beyond; no re-fogging
- A* uses the Manhattan heuristic
- Agent re-plans when new cells are revealed

## Documentation alignment
- Keep README, TEAM_API.md, docs/PEAS (slides), and module docstrings in sync with the above
