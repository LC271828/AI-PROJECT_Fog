# Team API and Interfaces (Scaffold)

Purpose
- Align modules, roles, and interfaces so teammates can code to contracts and re-plan cleanly.

Roles
- Gibran → Search + Metrics
- Asthar → Grid + Fog + Maps
- Ahsan → Agent + Heuristics
- Thomz → Visualisation + Demo
- Bayu → Docs + Slides
- Leo → Integrator / Release Manager

Branch workflow
- main (final, protected)
- dev (shared integration)

Module contracts

Types and conventions
- Coord: tuple[int, int]  # (row, col)
- Path: list[Coord]       # inclusive from start to goal; [] if no path
- Grid symbols: "0" free, "1" wall, "S" start, "G" goal
- Movement: Up/Down/Left/Right only (no diagonals)
- Visibility: radius 1; walls are visible when adjacent and block reveal beyond; no re-fogging

Grid (src/grid.py)
- from_csv(path: PathLike) -> Grid
- fields:
  - grid: list[list[str]]           # as read from CSV (no artificial borders)
  - start: Coord
  - goal:  Coord
  - visible: list[list[bool]]       # same shape as grid; all False initially
  - width: int; height: int; fog_radius: int = 1
- methods:
  - in_bounds(r: int, c: int) -> bool
  - passable(r: int, c: int) -> bool
  - neighbors4(r: int, c: int) -> list[Coord]
  - tile_at(r: int, c: int) -> str
  - is_visible(r: int, c: int) -> bool
  - reveal_from(pos: Coord) -> list[Coord]
      - reveals current cell and up to one cell in each cardinal direction; returns newly revealed coords
  - get_visible_neighbors(pos: Coord) -> list[Coord]
  - visible_tiles() -> list[Coord]

Search (src/search.py)
- bfs(grid, start: Coord, goal: Coord) -> Path
- dfs(grid, start: Coord, goal: Coord) -> Path
- ucs(grid, start: Coord, goal: Coord) -> Path
- astar(grid, start: Coord, goal: Coord, h=manhattan) -> Path
- ALGORITHMS: dict[str, callable]

Agent (src/agent.py)
- Metrics dataclass: steps, nodes_expanded, replans, runtime
- OnlineAgent(grid, algo="astar") with:
  - step() -> bool            # False when finished; True otherwise
  - run(max_steps: int = 10000) -> Metrics
  - re-plan when new cells are revealed
  - calls `grid.reveal_from(current_pos)` each step (fog handled by Grid)

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
