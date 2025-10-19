# AI Mini Project: Fog Maze (Scaffold)

This repository is a scaffold for the Fog Maze Game — an AI mini-project demonstrating a search-based agent under partial observability (UGM AI).

Context and goals:
- Agent operates on a grid maze with fog-of-war (limited visibility, no re-fogging).
- Showcases searching (DFS, BFS, UCS, A*) and online agents (perceive → plan → act).
- PEAS: Reach goal efficiently; discrete grid; actions Up/Down/Left/Right; perceive local neighborhood.

What’s included:
- Directory structure, placeholder modules, and TODOs only.
- Minimal docs and map example for reference.
 - Experiments sandbox: `experiments/` with per-teammate folders (keep production code in `src/`, tests in `tests/`).

Quick start for experiments:
- See `experiments/_template/quickstart.py` and the usage guide in `experiments/README.md`.

Next steps (high level):
1) Implement src/grid.py (CSV load, neighbors, visible)
2) Implement src/search.py (BFS/DFS/UCS/A* + ALGORITHMS)
3) Implement src/agent.py (OnlineAgent + Metrics)
4) Implement src/main.py (CLI) and optionally src/visualize.py (pygame)
5) Write tests in tests/ once modules are ready

See docs/ for assignment notes and decisions.
