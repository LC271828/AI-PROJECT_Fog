"""Lightweight search algorithms over a neighbor function.

Each function accepts ``start``, ``goal``, and a ``neighbors_fn(pos)`` callable
that yields adjacent coordinates. Algorithms return a list of coordinates
representing a path from start to goal (inclusive). Empty list indicates no path.
"""

from heapq import heappush, heappop
from collections import deque
from dataclasses import dataclass
import time


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


# Greedy Best-First Search: prioritizes heuristic only (no g-cost)
def greedy_neighbors(start, goal, neighbors_fn, h=manhattan):
    """Greedy Best-First Search over a neighbor function.

    Uses a priority queue ordered by h(n, goal) only. Not optimal in general,
    but often fast to reach the goal in open spaces.

    Returns a list of coordinates from start to goal (inclusive), or [] if no path exists.
    """
    frontier = []
    heappush(frontier, (h(start, goal), start))
    came_from = {}
    visited = {start}

    while frontier:
        _, current = heappop(frontier)
        if current == goal:
            return reconstruct_path(came_from, start, goal)

        for neighbor in neighbors_fn(current):
            if neighbor in visited:
                continue
            visited.add(neighbor)
            came_from[neighbor] = current
            heappush(frontier, (h(neighbor, goal), neighbor))

    return []

# Export dictionary used by CLI/tests to select algorithms by name
ALGORITHMS_NEIGHBORS = {
    "bfs": bfs_neighbors,
    "dfs": dfs_neighbors,
    "ucs": ucs_neighbors,
    "astar": astar_neighbors,
    "greedy": greedy_neighbors,
}


# Leo: Minimal stats support without rewriting existing algorithms.
# We wrap the provided neighbors_fn to count how many times a node is expanded
# (each call corresponds to an expansion in these algorithms), and time the run.
@dataclass
class SearchResult:
    path: list
    nodes_expanded: int
    runtime: float
    cost: int


def _with_stats(search_func, start, goal, neighbors_fn, **kwargs):
    """Run ``search_func`` with a counted neighbor function and basic timing.

    Returns a SearchResult with path, nodes_expanded (number of expansions),
    runtime in seconds, and unit-cost path cost.
    """
    # Count how many times the algorithm expands a node (calls neighbors_fn)
    count = {"n": 0}

    def counted_neighbors(pos):
        count["n"] += 1
        return neighbors_fn(pos)

    t0 = time.time()
    path = search_func(start, goal, counted_neighbors, **kwargs)
    runtime = time.time() - t0
    # More readable than a conditional expression
    if path:
        cost = max(0, len(path) - 1)
    else:
        cost = 0
    return SearchResult(path=path, nodes_expanded=count["n"], runtime=runtime, cost=cost)


def bfs_neighbors_with_stats(start, goal, neighbors_fn):
    """Leo: Wrapper that collects basic metrics for BFS without modifying BFS itself."""
    return _with_stats(bfs_neighbors, start, goal, neighbors_fn)


def dfs_neighbors_with_stats(start, goal, neighbors_fn):
    """Leo: Wrapper that collects basic metrics for DFS without modifying DFS itself."""
    return _with_stats(dfs_neighbors, start, goal, neighbors_fn)


def ucs_neighbors_with_stats(start, goal, neighbors_fn):
    """Leo: Wrapper that collects basic metrics for UCS without modifying UCS itself."""
    return _with_stats(ucs_neighbors, start, goal, neighbors_fn)


def astar_neighbors_with_stats(start, goal, neighbors_fn, h=manhattan):
    """Leo: Wrapper that collects basic metrics for A* without modifying A* itself."""
    return _with_stats(astar_neighbors, start, goal, neighbors_fn, h=h)


ALGORITHMS_NEIGHBORS_WITH_STATS = {
    "bfs": bfs_neighbors_with_stats,
    "dfs": dfs_neighbors_with_stats,
    "ucs": ucs_neighbors_with_stats,
    "astar": astar_neighbors_with_stats,
    "greedy": None,  # filled below with a named function for readability
}


def greedy_neighbors_with_stats(start, goal, neighbors_fn):
    """Wrapper collecting metrics for Greedy Best-First Search."""
    return _with_stats(greedy_neighbors, start, goal, neighbors_fn, h=manhattan)


# Fill the mapping with the named function instead of a lambda
ALGORITHMS_NEIGHBORS_WITH_STATS["greedy"] = greedy_neighbors_with_stats

