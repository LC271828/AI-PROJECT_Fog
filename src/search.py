"""Search algorithms (TODO-only scaffold).

Planned pure functions (no pygame, no I/O):
- bfs(start, goal, neighbors) -> path
- dfs(start, goal, neighbors) -> path
- ucs(start, goal, neighbors, cost=unit) -> path
- astar(start, goal, neighbors, h=manhattan, cost=unit) -> path

Contracts:
- Inputs are coordinates (row, col) and a neighbor function returning iterable of coordinates.
- Output is a list of coordinates from start to goal (inclusive). Empty if no path.

Next steps:
- Implement each algorithm and a small reconstruct(came_from) helper.
- Provide ALGORITHMS dict mapping names to callables.
"""

# TODO: implement bfs, dfs, ucs, astar and ALGORITHMS mapping.
