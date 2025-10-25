"""Lightweight search algorithms over a neighbor function.

Each function accepts ``start``, ``goal``, and a ``neighbors_fn(pos)`` callable
that yields adjacent coordinates. Algorithms return a list of coordinates
representing a path from start to goal (inclusive). Empty list indicates no path.
"""

from heapq import heappush, heappop
from collections import deque


def manhattan(a, b):
    """Manhattan distance heuristic between grid coordinates ``a`` and ``b``."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def reconstruct_path(came_from, start, goal):
    """Rebuild the path from ``start`` to ``goal`` using a parent map.

    Parameters
    - came_from: dict mapping node -> predecessor node
    - start, goal: coordinates

    Returns a list of coordinates from start to goal (inclusive),
    or an empty list when no path exists.
    """
    path = []
    current = goal
    while current != start:
        if current not in came_from:
            return []  # no path
        path.append(current)
        current = came_from[current]
    path.append(start)
    path.reverse()
    return path


def bfs_neighbors(start, goal, neighbors_fn):
    """Breadth-First Search over a neighbor function.

    Returns a shortest path in unweighted graphs as a list of coordinates,
    or [] if no path exists.
    """
    queue = deque([start])
    came_from = {}
    visited = {start}

    while queue:
        current = queue.popleft()

        if current == goal:
            return reconstruct_path(came_from, start, goal)

        for neighbor in neighbors_fn(current):
            if neighbor not in visited:
                visited.add(neighbor)
                came_from[neighbor] = current
                queue.append(neighbor)

    return []


def dfs_neighbors(start, goal, neighbors_fn):
    """Depth-First Search over a neighbor function (not optimal in general)."""
    stack = [start]
    came_from = {}
    visited = {start}

    while stack:
        current = stack.pop()

        if current == goal:
            return reconstruct_path(came_from, start, goal)

        for neighbor in neighbors_fn(current):
            if neighbor not in visited:
                visited.add(neighbor)
                came_from[neighbor] = current
                stack.append(neighbor)

    return []


def ucs_neighbors(start, goal, neighbors_fn):
    """Uniform Cost Search (Dijkstra for unit edge cost = 1)."""
    frontier = []
    heappush(frontier, (0, start))
    came_from = {}
    cost_so_far = {start: 0}

    while frontier:
        cost, current = heappop(frontier)

        if current == goal:
            return reconstruct_path(came_from, start, goal)

        for neighbor in neighbors_fn(current):
            new_cost = cost_so_far[current] + 1  # uniform step cost
            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                cost_so_far[neighbor] = new_cost
                came_from[neighbor] = current
                heappush(frontier, (new_cost, neighbor))

    return []


def astar_neighbors(start, goal, neighbors_fn, h=manhattan):
    """A* Search using Manhattan heuristic by default."""
    frontier = []
    heappush(frontier, (0, start))
    came_from = {}
    g_score = {start: 0}

    while frontier:
        _, current = heappop(frontier)

        if current == goal:
            return reconstruct_path(came_from, start, goal)

        for neighbor in neighbors_fn(current):
            tentative_g = g_score[current] + 1
            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                g_score[neighbor] = tentative_g
                f_score = tentative_g + h(neighbor, goal)
                came_from[neighbor] = current
                heappush(frontier, (f_score, neighbor))

    return []


# Export dictionary used by CLI/tests to select algorithms by name
ALGORITHMS_NEIGHBORS = {
    "bfs": bfs_neighbors,
    "dfs": dfs_neighbors,
    "ucs": ucs_neighbors,
    "astar": astar_neighbors
}
