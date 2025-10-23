"""Search algorithms (TODO).

Canonical API: neighbor-function based (no pygame, no I/O)
- bfs_neighbors(start, goal, neighbors_fn) -> path
- dfs_neighbors(start, goal, neighbors_fn) -> path
- ucs_neighbors(start, goal, neighbors_fn) -> path
- astar_neighbors(start, goal, neighbors_fn, h=manhattan) -> path

Contracts:
- Inputs:
    - start, goal: coordinates as tuples (row, col)
    - neighbors_fn: Callable[[tuple[int,int]], list[tuple[int,int]]]
- Output: list of coordinates from start to goal (inclusive). Empty list if no path exists.

Notes:
- Keep algorithms side-effect free.
- If start == goal: return [start]. If start/goal is not passable under neighbors_fn, return [].
- Provide `ALGORITHMS_NEIGHBORS = {"bfs": bfs_neighbors, "dfs": dfs_neighbors, "ucs": ucs_neighbors, "astar": astar_neighbors}`.

With-stats variants (optional):
- Return `SearchResult` with fields: path, nodes_expanded, runtime, cost.

Next steps:
- Implement algorithms, a `reconstruct(came_from, start, goal)` helper, and Manhattan heuristic.
"""

# TODO: implement bfs_neighbors, dfs_neighbors, ucs_neighbors, astar_neighbors,
# ALGORITHMS_NEIGHBORS mapping, and optional with-stats variants.
