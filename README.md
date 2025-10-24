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
- Canonical API: neighbor-function search (plan on what you can see)
- Functions: DFS, BFS, UCS, A* (Manhattan)
- Agent re-plans when new cells are revealed, updating its known map and re-running search as needed

PEAS (high-level)
- Performance: path cost, nodes expanded, runtime
- Environment: static, deterministic, discrete, partially observable
- Actuators: move up/down/left/right
- Sensors: current cell + adjacent visibility (fog radius 1)

Structure
- Production: `src/` (grid.py: fog/visibility; search.py: neighbor-function search; agent.py: planning/re-planning; visualize.py: Pygame view; main.py: CLI)
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

## Demos (quick start)

We moved demos into `examples/` so they're easy to find and runnable as modules.

- Grid visibility demo
	- `python -m examples.demo_grid`
- Online agent demo (text-only)
	- `python -m examples.demo_agent`

Tips
- Run from the repository root so `src/` is on the import path.
- Alternatively, you can run them directly: `python examples/demo_grid.py`.

<!-- CHANGE: Moved the WithGUI setup command from the Demos tips section up into
     Dev quickstart (Windows) under the Optional GUI bullet to avoid confusion. -->

## Headless CLI

You can run a minimal headless CLI that loads `config.json` (overridden by flags), runs the agent, and prints metrics.

Examples (from repo root):
- `python -m src.main`  # uses `config.json` (default map, algo=astar, fog on)
- `python -m src.main --map maps/demo.csv --algo bfs --no-fog`

Flags
- `--config` path to JSON config (default: `config.json`)
- `--map` CSV map path (overrides config)
- `--algo` one of bfs|dfs|ucs|astar (overrides config)
- `--no-fog` disable fog (agent has full map)
- `--fog` enable fog (default if config has fog_radius > 0)
- `--gui` accepted but not implemented yet (prints a notice)

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

Tiny example (planning under fog)
```python
from src.grid import Grid
from src.search import astar_neighbors

g = Grid.from_csv("maps/demo.csv")
g.reveal_from(g.start)

def visible_neighbors(rc):
	return g.get_visible_neighbors(rc)

path = astar_neighbors(g.start, g.goal, visible_neighbors)
print(len(path))  # None or steps
```

Next steps (high level)
1) Implement `src/grid.py` (CSV load, neighbors, visibility — no artificial borders)
2) Implement `src/search.py` (DFS/BFS/UCS/A* via neighbor-function APIs + optional with-stats)
3) Implement `src/agent.py` (OnlineAgent, re-planning, Metrics; build neighbors_fn from `grid.get_visible_neighbors`)
4) Implement `src/main.py` (CLI) and optionally `src/visualize.py` (Pygame)
5) Write tests in `tests/` after modules are ready

See `docs/` for assignment notes and decisions.
