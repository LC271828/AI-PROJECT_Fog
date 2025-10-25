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

- GUI visualizer (optional)
	- First install GUI dep: `powershell -ExecutionPolicy Bypass -File .\\scripts\\setup.ps1 -WithGUI`
	- Run via CLI: `python -m src.main --gui`
	- Or run the examples runner: `python -m examples.run_visualize`

## Interactive TUI (no flags)

With no flags and in an interactive terminal, running `python -m src.main` brings up a small menu:

- Choose mode: GUI (pygame) or Text (ASCII)
- If Text: pick a map (from `maps/*.csv`), algorithm, fog on/off, steps, delay, and with-stats

If pygame isn’t installed and you pick GUI, it falls back cleanly to Text mode.

Tips
- Run from the repository root so `src/` is on the import path.
- Alternatively, you can run them directly: `python examples/demo_grid.py`.

<!-- CHANGE: Moved the WithGUI setup command from the Demos tips section up into
     Dev quickstart (Windows) under the Optional GUI bullet to avoid confusion. -->

## Headless CLI

By default (when run with no flags), the project will open a TUI menu (on interactive terminals) or try GUI directly; if GUI isn’t available, it falls back to the headless CLI.

You can run a minimal headless CLI that loads `config.json` (overridden by flags), runs the agent, and prints metrics.

Examples (from repo root):
- `python -m src.main`  # uses `config.json` (default map, algo=astar, fog on)
- `python -m src.main --map maps/demo.csv --algo bfs --no-fog`
- `python -m src.main --map maps/demo.csv --algo astar --with-stats`  # collect nodes expanded + runtime

Flags
- `--config` path to JSON config (default: `config.json`)
- `--map` CSV map path (overrides config)
- `--algo` one of bfs|dfs|ucs|astar (overrides config)
- `--no-fog` disable fog (agent has full map)
- `--fog` enable fog (default if config has fog_radius > 0)
- `--with-stats` use metrics-enabled search (nodes expanded, runtime, cost)
- `--gui` launches the GUI visualizer (requires pygame; see GUI section below). When no flags are given, you’ll get a TUI on interactive terminals.

## Text visualization (ASCII)

You can render a masked, text-based view of the grid with overlays (agent `@`, plan `*`) without installing pygame. This is useful when you want CLI output that steps through frames.

Examples (from repo root):

- `python -m examples.visualize_text --map maps/demo.csv --algo astar --steps 50 --delay 0.25`
- Disable fog for a full-map run: `python -m examples.visualize_text --map maps/demo.csv --algo bfs --no-fog`

Notes
- Windows users can keep using PowerShell; commands above work the same.
- The interactive TUI uses the official `src.textviz` under the hood. For non-interactive runs, use the example module above or call `src.textviz.run_text_session` from your own scripts.

## GUI (optional)

The Pygame-based visualizer is optional and kept separate so tests and headless usage don’t require pygame.

Install (Windows PowerShell):

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\setup.ps1 -WithGUI
```

Alternatively (any platform):

```powershell
python -m pip install pygame
```

Run (from repo root):

- Via CLI (recommended):

```powershell
python -m src.main --gui
```

- Or the examples runner:

```powershell
python -m examples.run_visualize
```

Notes
- If pygame is missing, the CLI will print a friendly message with an install hint.
- Linux/macOS users can install GUI support with `WITH_GUI=1 ./scripts/setup.sh` and then run the same commands.

### GUI controls and HUD

- Menu
	- Up/Down: select map/algorithm (Tab switches column)
	- V: toggle Fog On/Off (Fog Off = full-map, like `--no-fog` in CLI)
	- + / -: adjust initial FPS (F to type a number directly, Enter to apply)
	- T: toggle metrics-enabled search (shows Nodes expanded + Runtime)
	- Enter: launch visualizer; Esc: quit menu

- Visualizer
	- Space: pause/play
	- N: single-step while paused
	- + / -: adjust FPS on the fly
	- Left/Right: navigate step history (when available); the left panel shows the counter
	- ESC or window close: exit

- HUD (top bar)
	- Left: Map name, Algorithm, Fog status
	- Center: Start, Goal, Grid size
	- Right: Steps, Replans, Nodes expanded (with stats on), Cost (cumulative), Runtime, FPS, and status

Rendering
- With fog: only visible tiles are shown; path taken and current plan are overlaid
- No fog: the entire map is drawn; overlays still show agent path and plan

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
2) Implement `src/search.py` (DFS/BFS/UCS/A* via neighbor-function APIs + optional with-stats wrappers)
3) Implement `src/agent.py` (OnlineAgent, re-planning, Metrics; build neighbors_fn from `grid.get_visible_neighbors`)
4) Implement `src/main.py` (CLI) and optionally `src/visualize.py` (Pygame)
5) Write tests in `tests/` after modules are ready

See `docs/` for assignment notes and decisions.

## Test output and troubleshooting

We enable per-test live logging and a rich terminal summary by default:

- Per-test banners: start/end lines with durations (from `tests/conftest.py`).
- Rich summary: totals and Top 5 slow tests (from `tests/pytest_rich_report.py`).

Run tests from repo root:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\test.ps1
```

Disable the pretty summary if needed:

```powershell
python -m pytest -p no:tests.pytest_rich_report
```

If you see “No module named pytest”, your shell is using a Python without dev deps.

- Ensure `.venv` is active and has requirements installed:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\setup.ps1
. .\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Then rerun tests.
