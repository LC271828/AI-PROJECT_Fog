# AI Mini Project — Fog Maze (UGM AI)

Simulation of an intelligent agent navigating a partially observable maze with fog-of-war.

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

Branch workflow
- `main` (final, protected) and `dev` (shared integration)

Team roles
- Gibran → Search + Metrics
- Asthar → Grid + Fog + Maps
- B → Agent + Heuristics
- C → Visualisation + Demo
- D → Docs + Slides
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
