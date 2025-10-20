# Team API and Interfaces (Scaffold)

Purpose
- Align modules, roles, and interfaces so teammates can code to contracts and re-plan cleanly.

Roles
- Gibran → Search + Metrics
- Asthar → Grid + Fog + Maps
- B → Agent + Heuristics
- C → Visualisation + Demo
- D → Docs + Slides
- Leo → Integrator / Release Manager

Branch workflow
- main (final) → dev (integration) → feat/... (feature branches)

Module contracts

Grid (src/grid.py)
- from_csv(path) -> Grid
- fields: grid, start, goal, visible, width, height, fog_radius(=1)
- methods:
  - in_bounds(r,c) -> bool
  - passable(r,c) -> bool
  - neighbors4(r,c) -> list[(r,c)]
  - tile_at(r,c) -> str
  - is_visible(r,c) -> bool
  - reveal_from(pos) -> None  # radius=1; walls revealed and block beyond; no re-fogging
  - get_visible_neighbors(pos) -> list[(r,c)]
  - visible_tiles() -> list[(r,c)]

Search (src/search.py)
- bfs(grid, start, goal) -> list[(r,c)] | []
- dfs(grid, start, goal) -> list[(r,c)] | []
- ucs(grid, start, goal) -> list[(r,c)] | []
- astar(grid, start, goal, h=manhattan) -> list[(r,c)] | []
- ALGORITHMS = {"bfs": bfs, "dfs": dfs, "ucs": ucs, "astar": astar}

Agent (src/agent.py)
- Metrics dataclass: steps, nodes_expanded, replans, runtime
- OnlineAgent(grid, algo="astar") with:
  - step() -> None
  - run() -> Metrics
  - re-plan when new cells are revealed

Visualisation (src/visualize.py)
- Optional Pygame renderer showing fog mask, visible walls, agent, path

CLI (src/main.py)
- load_config -> dict
- main(argv) -> int
- parse: --map, --algo, --gui, --fog (fixed to 1 in this project)

Consistency
- Movement: U/D/L/R only
- Visibility: radius 1; walls block reveal beyond; no re-fog
- Heuristic: Manhattan for A*
