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
