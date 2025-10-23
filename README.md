# AI Mini Project — Fog Maze (UGM AI)

Simulation of an intelligent agent navigating a partially observable maze with fog-of-war.

## TL;DR

- Where to code:
	- Grid/Fog → `src/grid.py`
	- Search → `src/search.py`
	- Agent → `src/agent.py`
- Setup once (Windows):
	- `powershell -ExecutionPolicy Bypass -File .\\scripts\\setup.ps1`
- Run tests anytime:
	- `powershell -ExecutionPolicy Bypass -File .\\scripts\\test.ps1`
- Push to `dev` when tests pass.
- Optional GUI deps (pygame) if working on visualization:
	- `powershell -ExecutionPolicy Bypass -File .\\scripts\\setup.ps1 -WithGUI`

Quick commit and push to dev (Windows):
- `git add .`
- `git commit -m "work in progress"`
- `git push origin HEAD:dev`

Context
- Course: UGM Artificial Intelligence
- Team: 6 members (see roles below)
- Environment: static, deterministic, discrete, partially observable
- Movement: up/down/left/right (no diagonals)
- Visibility: radius 1 in four directions; walls are visible when adjacent and block reveal beyond; no re-fogging
- Start and goal are known; map layout is initially hidden by fog

Algorithms
- Classical search: DFS, BFS, UCS, A*
- Heuristic: A* uses Manhattan distance
- Agent re-plans when new cells are revealed, updating its known map and re-running search as needed

PEAS (high-level)
- Performance: path cost, nodes expanded, runtime
- Environment: static, deterministic, discrete, partially observable
- Actuators: move up/down/left/right
- Sensors: current cell + adjacent visibility (fog radius 1)

Structure
- Production: `src/` (grid.py: fog/visibility; search.py: search logic; agent.py: planning/re-planning; visualize.py: Pygame view; main.py: CLI)
- Tests: `tests/`
- Maps: `maps/`
- Docs: `docs/`
- Experiments: `experiments/` per teammate (do not import from experiments inside src/tests)

Dev quickstart (Windows)
- Create virtual environment and install dev deps:
	- `powershell -ExecutionPolicy Bypass -File .\\scripts\\setup.ps1`
- Run tests:
	- `powershell -ExecutionPolicy Bypass -File .\\scripts\\test.ps1`
- Optional: include GUI dependency (pygame) if working on visualization:
	- `powershell -ExecutionPolicy Bypass -File .\\scripts\\setup.ps1 -WithGUI`

Dev quickstart (Linux/macOS)
- Setup virtual environment and install deps:
	- `./scripts/setup.sh` (or `WITH_GUI=1 ./scripts/setup.sh` to add pygame)
- Run tests:
	- `./scripts/test.sh`
- Note: If you prefer PowerShell on Linux, use `pwsh -File ./scripts/setup.ps1`.

Branch workflow
- Work on `dev` by default (commit/push directly to `dev`).
- If a specific bug/feature is risky or large, create a short-lived branch from `dev`, then open a PR into `dev`.
- Only the coordinator (Leo) merges `dev` → `main` (main is protected).

Team roles
- Gibran → Search + Metrics
- Asthar → Grid + Fog + Maps
- Ahsan → Agent + Heuristics
 - Thomz → Visualisation + Co-Presenter (demo engineer; supports others as needed)
- Bayu → Presentation Lead + Support (Slides; demo owner; helps wherever needed)
- Leo → Integrator / Release Manager

What’s included now
- Scaffold (placeholders and TODOs), minimal docs, and example map
- Experiments sandbox with per-teammate folders and a quickstart template

Quick start for experiments
- See `experiments/_template/quickstart.py` and the usage guide in `experiments/README.md`.

Next steps (high level)
1) Implement `src/grid.py` (CSV load, neighbors, visibility)
2) Implement `src/search.py` (DFS/BFS/UCS/A* + ALGORITHMS)
3) Implement `src/agent.py` (OnlineAgent, re-planning, Metrics)
4) Implement `src/main.py` (CLI) and optionally `src/visualize.py` (Pygame)
5) Write tests in `tests/` after modules are ready

See `docs/` for assignment notes and decisions.
