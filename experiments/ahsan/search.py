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
from typing import Callable, Iterable, List, Tuple, Optional

Coord = Tuple[int, int]
Path = List[Coord]


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
