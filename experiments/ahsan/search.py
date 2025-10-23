"""Small search utilities adapted for experiments.

These functions are generic: they accept a neighbor function so the agent
can provide a view-limited neighbor function (for fog) or a full-map
neighbor function (for full visibility).

API:
  bfs(start, goal, neighbors) -> Path (list of coords) or [] if no path
  astar(start, goal, neighbors, h=manhattan) -> Path or []

Coord is tuple[int,int].
"""
from collections import deque
from heapq import heappush, heappop
from typing import Callable, Iterable, List, Tuple, Optional, NamedTuple
import time

Coord = Tuple[int, int]
Path = List[Coord]


class SearchResult(NamedTuple):
    path: Path
    nodes_expanded: int
    runtime: float
    cost: int


def reconstruct(came_from: dict, current: Coord) -> Path:
    path = [current]
    while current in came_from:
        current = came_from[current]
        path.append(current)
    path.reverse()
    return path


def bfs(start: Coord, goal: Coord, neighbors: Callable[[Coord], Iterable[Coord]]) -> Path:
    if start == goal:
        return [start]
    frontier = deque([start])
    came_from: dict[Coord, Coord] = {}
    visited = {start}

    while frontier:
        current = frontier.popleft()
        for n in neighbors(current):
            if n in visited:
                continue
            visited.add(n)
            came_from[n] = current
            if n == goal:
                return reconstruct(came_from, n)
            frontier.append(n)
    return []


def bfs_with_stats(start: Coord, goal: Coord, neighbors: Callable[[Coord], Iterable[Coord]]) -> SearchResult:
    start_time = time.time()
    if start == goal:
        return SearchResult([start], 0, 0.0, 0)
    frontier = deque([start])
    came_from: dict[Coord, Coord] = {}
    visited = {start}
    nodes_expanded = 0

    while frontier:
        current = frontier.popleft()
        nodes_expanded += 1
        for n in neighbors(current):
            if n in visited:
                continue
            visited.add(n)
            came_from[n] = current
            if n == goal:
                path = reconstruct(came_from, n)
                runtime = time.time() - start_time
                cost = len(path) - 1
                return SearchResult(path, nodes_expanded, runtime, cost)
            frontier.append(n)
    runtime = time.time() - start_time
    return SearchResult([], nodes_expanded, runtime, 0)


def manhattan(a: Coord, b: Coord) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def astar(start: Coord, goal: Coord, neighbors: Callable[[Coord], Iterable[Coord]], h: Callable[[Coord, Coord], float] = manhattan) -> Path:
    if start == goal:
        return [start]
    open_heap: list[Tuple[float, Coord]] = []
    g_score: dict[Coord, float] = {start: 0}
    f_score: dict[Coord, float] = {start: h(start, goal)}
    came_from: dict[Coord, Coord] = {}

    heappush(open_heap, (f_score[start], start))
    open_set = {start}

    while open_heap:
        _, current = heappop(open_heap)
        if current == goal:
            return reconstruct(came_from, current)
        open_set.discard(current)

        for n in neighbors(current):
            tentative_g = g_score[current] + 1
            if n not in g_score or tentative_g < g_score[n]:
                came_from[n] = current
                g_score[n] = tentative_g
                f = tentative_g + h(n, goal)
                f_score[n] = f
                if n not in open_set:
                    heappush(open_heap, (f, n))
                    open_set.add(n)
    return []


def astar_with_stats(start: Coord, goal: Coord, neighbors: Callable[[Coord], Iterable[Coord]], h: Callable[[Coord, Coord], float] = manhattan) -> SearchResult:
    start_time = time.time()
    if start == goal:
        return SearchResult([start], 0, 0.0, 0)
    open_heap: list[Tuple[float, Coord]] = []
    g_score: dict[Coord, float] = {start: 0}
    f_score: dict[Coord, float] = {start: h(start, goal)}
    came_from: dict[Coord, Coord] = {}

    heappush(open_heap, (f_score[start], start))
    open_set = {start}
    nodes_expanded = 0

    while open_heap:
        _, current = heappop(open_heap)
        nodes_expanded += 1
        if current == goal:
            path = reconstruct(came_from, current)
            runtime = time.time() - start_time
            cost = len(path) - 1
            return SearchResult(path, nodes_expanded, runtime, cost)
        open_set.discard(current)

        for n in neighbors(current):
            tentative_g = g_score[current] + 1
            if n not in g_score or tentative_g < g_score[n]:
                came_from[n] = current
                g_score[n] = tentative_g
                f = tentative_g + h(n, goal)
                f_score[n] = f
                if n not in open_set:
                    heappush(open_heap, (f, n))
                    open_set.add(n)
    runtime = time.time() - start_time
    return SearchResult([], nodes_expanded, runtime, 0)


# Convenience mappings
ALGORITHMS = {
    "bfs": bfs,
    "astar": astar,
}

ALGORITHMS_WITH_STATS = {
    "bfs": bfs_with_stats,
    "astar": astar_with_stats,
}


def dfs(start: Coord, goal: Coord, neighbors: Callable[[Coord], Iterable[Coord]]) -> Path:
    """Depth-first search (iterative, stack-based). Returns a path or [] if none."""
    if start == goal:
        return [start]
    stack = [start]
    came_from: dict[Coord, Coord] = {}
    visited = {start}

    while stack:
        current = stack.pop()
        for n in neighbors(current):
            if n in visited:
                continue
            visited.add(n)
            came_from[n] = current
            if n == goal:
                return reconstruct(came_from, n)
            # push to stack to explore deeper
            stack.append(n)
    return []


def dfs_with_stats(start: Coord, goal: Coord, neighbors: Callable[[Coord], Iterable[Coord]]) -> SearchResult:
    start_time = time.time()
    if start == goal:
        return SearchResult([start], 0, 0.0, 0)
    stack = [start]
    came_from: dict[Coord, Coord] = {}
    visited = {start}
    nodes_expanded = 0

    while stack:
        current = stack.pop()
        nodes_expanded += 1
        for n in neighbors(current):
            if n in visited:
                continue
            visited.add(n)
            came_from[n] = current
            if n == goal:
                path = reconstruct(came_from, n)
                runtime = time.time() - start_time
                cost = len(path) - 1
                return SearchResult(path, nodes_expanded, runtime, cost)
            stack.append(n)
    runtime = time.time() - start_time
    return SearchResult([], nodes_expanded, runtime, 0)


def ucs(start: Coord, goal: Coord, neighbors: Callable[[Coord], Iterable[Coord]]) -> Path:
    """Uniform-cost search (Dijkstra) with unit edge costs.
    Returns a path or [] if none.
    """
    if start == goal:
        return [start]
    open_heap: list[Tuple[int, Coord]] = []
    g_score: dict[Coord, int] = {start: 0}
    came_from: dict[Coord, Coord] = {}

    heappush(open_heap, (0, start))
    closed = set()

    while open_heap:
        g, current = heappop(open_heap)
        if current in closed:
            continue
        closed.add(current)
        if current == goal:
            return reconstruct(came_from, current)
        for n in neighbors(current):
            tentative_g = g + 1
            if n not in g_score or tentative_g < g_score[n]:
                came_from[n] = current
                g_score[n] = tentative_g
                heappush(open_heap, (tentative_g, n))
    return []


def ucs_with_stats(start: Coord, goal: Coord, neighbors: Callable[[Coord], Iterable[Coord]]) -> SearchResult:
    start_time = time.time()
    if start == goal:
        return SearchResult([start], 0, 0.0, 0)
    open_heap: list[Tuple[int, Coord]] = []
    g_score: dict[Coord, int] = {start: 0}
    came_from: dict[Coord, Coord] = {}

    heappush(open_heap, (0, start))
    closed = set()
    nodes_expanded = 0

    while open_heap:
        g, current = heappop(open_heap)
        if current in closed:
            continue
        nodes_expanded += 1
        closed.add(current)
        if current == goal:
            path = reconstruct(came_from, current)
            runtime = time.time() - start_time
            cost = len(path) - 1
            return SearchResult(path, nodes_expanded, runtime, cost)
        for n in neighbors(current):
            tentative_g = g + 1
            if n not in g_score or tentative_g < g_score[n]:
                came_from[n] = current
                g_score[n] = tentative_g
                heappush(open_heap, (tentative_g, n))
    runtime = time.time() - start_time
    return SearchResult([], nodes_expanded, runtime, 0)


# Update mappings with new algorithms
ALGORITHMS.update({
    "dfs": dfs,
    "ucs": ucs,
})

ALGORITHMS_WITH_STATS.update({
    "dfs": dfs_with_stats,
    "ucs": ucs_with_stats,
})
