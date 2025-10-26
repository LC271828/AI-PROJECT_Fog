# Assignment Summary — Fog Maze (UGM AI)

Goal
- Build an AI agent that navigates a maze under partial observability (fog-of-war) with visibility radius 1.
- Compare classic search algorithms (BFS, DFS, UCS, A*) and a Greedy baseline.
- Provide a simple CLI, an optional GUI, and clear APIs so the team can work in parallel.

PEAS (short)
- Performance: steps (path cost), nodes expanded, runtime, replans.
- Environment: static, deterministic, discrete, partially observable.
- Actuators: move up/down/left/right.
- Sensors: current tile and adjacent tiles; walls block further reveal.

What we implemented
- Grid with strict CSV loading and fog-of-war helpers (`src/grid.py`).
- Search algorithms as pure neighbor-function planners with with‑stats wrappers (`src/search.py`).
- OnlineAgent that perceives, plans, and acts with re-planning under fog (`src/agent.py`).
- Headless CLI and a small TUI with an optional Pygame visualizer (`src/main.py`, `src/tui.py`, `src/visualize.py`).
- Text visualization utilities and demos under `examples/`.
- Benchmarks for scaling and comparisons (`scripts/bench.py`) and plotting helpers.

How to run (Windows PowerShell)
1) Setup once
	- `powershell -ExecutionPolicy Bypass -File .\\scripts\\setup.ps1`
	- Optional GUI: `powershell -ExecutionPolicy Bypass -File .\\scripts\\setup.ps1 -WithGUI`
2) Run tests
	- `powershell -ExecutionPolicy Bypass -File .\\scripts\\test.ps1`
3) Try the CLI
	- `python -m src.main --map maps/demo.csv --algo astar --with-stats`
4) Text demo
	- `python -m examples.visualize_text --map maps/demo.csv --algo bfs`
5) GUI (optional)
	- `python -m src.main --gui`

Notes
- Movement is 4-connected; A* uses Manhattan heuristic.
- No artificial borders are added to maps; CSV shape is the grid shape.
- The agent re-plans whenever new cells are revealed or a planned step becomes blocked.

See also
- README.md (context, roles, workflow)
- docs/PEAS.md (PEAS)
- TEAM_API.md (interfaces)
