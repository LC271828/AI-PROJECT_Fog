"""Search algorithms (TODO).

Planned pure functions (no pygame, no I/O), grid-first API:
- bfs(grid, start, goal) -> path
- dfs(grid, start, goal) -> path
- ucs(grid, start, goal) -> path
- astar(grid, start, goal, h=manhattan) -> path

Contracts:
- Inputs:
	- grid: a Grid-like object exposing `neighbors4(r,c)` and `passable(r,c)` (see TEAM_API.md)
	- start, goal: coordinates as tuples (row, col)
- Output: list of coordinates from start to goal (inclusive). Empty list if no path exists.

Notes:
- Keep algorithms side-effect free; do not mutate `grid`.
- Provide `ALGORITHMS = {"bfs": bfs, "dfs": dfs, "ucs": ucs, "astar": astar}`.

Next steps:
- Implement each algorithm and a small `reconstruct(came_from, start, goal)` helper.
- Use Manhattan distance for A*.
"""

# TODO: implement bfs, dfs, ucs, astar and ALGORITHMS mapping.
