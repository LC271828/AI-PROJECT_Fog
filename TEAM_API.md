# Team API and Interfaces (Transition-friendly)

Purpose
- Align modules, roles, and interfaces so teammates can code to contracts and re-plan cleanly.

TL;DR quick start (lowest-friction for experiments)
- You can call search either with a Grid or with a simple neighbor function. Both are supported.
- Grid does NOT add artificial borders; load CSV as-is. If your experiment added borders, keep it, but adapt via a thin view (example below).
- Fog is radius 1. Reveal is handled by Grid.reveal_from(pos). Agent calls it each step.
- Metrics: keep algorithms pure by default, but “with-stats” variants are provided in the API contract.

Roles
- Gibran → Search + Metrics
- Asthar → Grid + Fog + Maps
- Ahsan → Agent + Heuristics
- Thomz → Visualisation + Co-Presenter (demo engineer; assists teammates as needed)
- Bayu → Presentation Lead + Support (Slides; demo owner; assists teammates as needed)
# Team API (Simple English)

This file explains how our code works together. It uses short, simple sentences. It also shows small code examples for quick copy–paste.

What we are building
- A grid (CSV map) with fog-of-war.
- An agent that can see radius 1 (up/down/left/right), moves step by step, and re-plans.
- Search algorithms: DFS, BFS, UCS, A* (Manhattan).
- Optional GUI.

Quick start
- You can use two ways to run search:
  1) Grid-based API (simple)
  2) Neighbor-function API (easy for experiments)
- Fog: call `grid.reveal_from(pos)` every step.
- Metrics: use “with-stats” variants when you need nodes expanded and runtime; otherwise use the simple functions.

Which API should I use?
- Grid-based API: good for offline/full map tests and simple code.
- Neighbor-function API: best for planning on the visible subgraph under fog.
- With-stats variants: use when you need metrics (PEAS).

Links
- Maps format: maps/README.md
- PEAS: docs/PEAS.md
- Project README: README.md

Words we use (Glossary)
- Coord: (row, col) like (r, c)
- Path: list of Coord, from start to goal, inclusive
- Cost: number of steps on unit-cost maps (cost = len(path) - 1)
- Symbols: "0" free, "1" wall, "S" start, "G" goal

Rules
- Movement: Up, Down, Left, Right only (no diagonals).
- Visibility: radius 1 (current cell + 4 directions). Walls can be visible but are not passable. No re-fog.
- Heuristic (A*): Manhattan distance h(a,b) = |ra-rb| + |ca-cb|. We assume unit costs.

## Grid (src/grid.py)

What it holds (fields)
- grid: list[list[str]] — from CSV (no artificial borders)
- start: Coord
- goal: Coord
- visible: list[list[bool]] — same size as grid; all False at start
- width: int; height: int; fog_radius: int = 1

What it does (methods)
- from_csv(path) -> Grid
- in_bounds(r, c) -> bool
- passable(r, c) -> bool
- neighbors4(r, c) -> list[Coord]
- tile_at(r, c) -> str
- is_visible(r, c) -> bool
- reveal_from(pos: Coord) -> list[Coord]
  - Mark current cell and up to one cell in U/D/L/R as visible
  - Return only the newly revealed cells
- get_visible_neighbors(pos: Coord) -> list[Coord]
  - Only neighbors that are in bounds, visible, and passable
- visible_tiles() -> list[Coord]

Errors (be strict)
- CSV must be rectangular → raise ValueError otherwise
- Only these symbols: 0, 1, S, G → raise ValueError on others (say row/col)
- Exactly one S and one G → raise ValueError otherwise

No borders
- Do not add fake wall borders to the map.
- If your experiment added borders, do not change production Grid. Instead, use a small adapter or a neighbors function that respects in-bounds.

Small example (Grid)
```python
from src.grid import Grid

grid = Grid.from_csv("maps/demo.csv")
grid.reveal_from(grid.start)

print(grid.width, grid.height)
print(grid.visible_tiles())
```

## Search (src/search.py)

Canonical API (neighbor-function)
```python
def neighbors_fn(rc):
  return grid.get_visible_neighbors(rc)

path = astar_neighbors(grid.start, grid.goal, neighbors_fn)  # or bfs_neighbors/ucs_neighbors/dfs_neighbors
```

With-stats (metrics) variants
- Type: SearchResult
  - path: Path
  - nodes_expanded: int
  - runtime: float (seconds)
  - cost: int (usually len(path) - 1)
- API shape matches the neighbor-function style and exposes a mapping:
  - `ALGORITHMS_NEIGHBORS_WITH_STATS = {"bfs": bfs_neighbors_with_stats, ...}`
- Example:
```python
from src.search import ALGORITHMS_NEIGHBORS_WITH_STATS as SEARCH_WITH_STATS

def neighbors_fn(rc):
  return grid.get_visible_neighbors(rc)

res = SEARCH_WITH_STATS["astar"](grid.start, grid.goal, neighbors_fn)
print(res.nodes_expanded, res.runtime, res.cost)
```

Notes
- Algorithms must not change the Grid.
- If start == goal → return [start]. If start/goal is not passable → return [].
- Provide a mapping like ALGORITHMS_NEIGHBORS = {"bfs": bfs_neighbors, "dfs": dfs_neighbors, "ucs": ucs_neighbors, "astar": astar_neighbors}

Optional: offline baseline (no fog)
- You may create a tiny wrapper for offline tests:
```python
def astar_offline(grid):
  return astar_neighbors(grid.start, grid.goal, grid.neighbors4)
```

## Agent (src/agent.py)

Metrics (dataclass)
- steps: int
- nodes_expanded: int
- replans: int
- runtime: float (seconds)
- cost: int

OnlineAgent(grid, algo="astar")
- step() -> bool  (False when finished)
- run(max_steps=10000) -> Metrics
- Calls `grid.reveal_from(current_pos)` every step
- Re-plan when new cells are revealed

Plan under fog
- Build a neighbors_fn using `grid.get_visible_neighbors` and call search.
- If no path to goal is known yet, pick a frontier (a visible free cell next to unknown) and plan to it.
- After each move, if something changed (new info or blocked), re-plan.

## Visualize (src/visualize.py)

- Optional Pygame view: shows fog mask, visible walls, agent, and planned path.

## CLI (src/main.py)

- load_config() -> dict
- main(argv) -> int
- Args: --map, --algo, --gui, --fog (use 1 in this project)

## Consistency checklist

- Movement: U/D/L/R only
- Visibility: radius 1; walls can be visible but are not passable; no re-fog
- Heuristic: Manhattan (unit-cost)
- CSV shape = Grid shape (no extra borders)

## Migrate from experiments

- If you used neighbor functions → map to `bfs_neighbors` / `astar_neighbors`.
- If you revealed inside Agent → move reveal to `Grid.reveal_from(pos)`; keep your re-plan logic.
- If you added a border in your prototype → remove it in production; if needed, use a small adapter.
- If you collected nodes expanded/runtime → use the with-stats variants and `SearchResult`.
