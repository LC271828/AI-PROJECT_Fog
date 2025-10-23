"""Experimental OnlineAgent for development in experiments/ahsan.

This agent is intentionally kept in experiments so it can iterate quickly
without touching `src/`.

Usage: run this module or import OnlineAgent in experiments for manual tests.
It supports two modes:
  - full_map=True: agent has complete knowledge of the map at start (fast testing)
  - full_map=False: agent uses a simple reveal_from implementation that looks up
    neighbors from the Asthar grid and reveals only immediate adjacent tiles
    (simulates fog radius=1). This is enough to implement online replanning.

The agent uses `experiments/ahsan/search.py` functions (bfs/astar) which accept
an agent-provided neighbor function based on the agent's known free tiles.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, List, Tuple, Set
from pathlib import Path
import time

# Import Asthar's experiment Grid reader (used as the authoritative map for now)
from experiments.asthar.grid import Grid as Grid
from experiments.ahsan.search import bfs, astar, Coord, Path

Coord = Tuple[int, int]


@dataclass
class Metrics:
    start: Coord
    goal: Coord
    steps: int = 0
    replans: int = 0
    reached_goal: bool = False
    path_taken: List[Coord] = None

    def __post_init__(self):
        if self.path_taken is None:
            self.path_taken = [self.start]


class OnlineAgent:
    def __init__(self, grid_path: Path, full_map: bool = True, search_algo: Callable = astar):
        self.impl = Grid(map=grid_path)
        # normalize start/goal to tuples
        self.start: Coord = tuple(self.impl.start)
        self.goal: Coord = tuple(self.impl.goal)
        self.current: Coord = self.start
        self.full_map = full_map
        self.search = search_algo

        # known tiles maintained by agent
        self.known_passable: Set[Coord] = set()
        self.known_walls: Set[Coord] = set()
        # initialize known tiles if full_map
        if self.full_map:
            for r in range(self.impl.height):
                for c in range(self.impl.width):
                    pos = (r, c)
                    # Asthar grid stores strings like '0' and '1' and may have extra border
                    try:
                        tile = self.impl.grid[r][c]
                    except Exception:
                        continue
                    if tile == '1':
                        self.known_walls.add(pos)
                    else:
                        self.known_passable.add(pos)
        else:
            # reveal starting cell and its neighbors (simulate fog radius=1)
            self._reveal_from(self.start)

        self.metrics = Metrics(start=self.start, goal=self.goal)
        self.current_plan: List[Coord] = []

    # --- perception helpers (experimental wrappers around Grid) ---
    def _in_bounds(self, pos: Coord) -> bool:
        r, c = pos
        return 0 <= r < self.impl.height and 0 <= c < self.impl.width

    def _tile_at(self, pos: Coord) -> str:
        r, c = pos
        return self.impl.grid[r][c]

    def _reveal_from(self, pos: Coord) -> List[Coord]:
        """Reveal pos and its 4-neighbors from the authoritative Asthar grid.
        Returns list of newly revealed coords (tuples).
        This is a small simulation of fog radius=1.
        """
        newly = []
        for d in [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]:
            p = (pos[0] + d[0], pos[1] + d[1])
            if not self._in_bounds(p):
                continue
            if p in self.known_passable or p in self.known_walls:
                continue
            tile = self._tile_at(p)
            if tile == '1':
                self.known_walls.add(p)
            else:
                self.known_passable.add(p)
            newly.append(p)
        return newly

    # --- neighbor function used by search algorithms ---
    def known_neighbors(self, pos: Coord) -> Iterable[Coord]:
        # deterministic neighbor order: Up, Right, Down, Left
        for dr, dc in [(-1, 0), (0, 1), (1, 0), (0, -1)]:
            n = (pos[0] + dr, pos[1] + dc)
            if n in self.known_passable:
                yield n

    # --- planning/execution ---
    def plan_to(self, target: Coord) -> List[Coord]:
        path = self.search(self.current, target, lambda p: self.known_neighbors(p))
        return path

    def choose_frontier(self) -> Coord | None:
        """Return the nearest known passable cell that has at least one unknown neighbor.
        Simple BFS on known graph.
        """
        from collections import deque

        visited = {self.current}
        q = deque([self.current])
        while q:
            cur = q.popleft()
            # check if cur is a frontier
            for dr, dc in [(-1, 0), (0, 1), (1, 0), (0, -1)]:
                nb = (cur[0] + dr, cur[1] + dc)
                if not self._in_bounds(nb):
                    continue
                if nb not in self.known_passable and nb not in self.known_walls:
                    return cur
            # otherwise expand
            for n in self.known_neighbors(cur):
                if n not in visited:
                    visited.add(n)
                    q.append(n)
        return None

    def step(self) -> bool:
        """Perform one perception-plan-act cycle. Returns False when done.
        """
        # Perceive
        if not self.full_map:
            self._reveal_from(self.current)

        # If at goal
        if self.current == self.goal:
            self.metrics.reached_goal = True
            return False

        # Ensure we have a plan
        if not self.current_plan:
            # Try plan to goal
            path = self.plan_to(self.goal)
            if path:
                self.current_plan = path
            else:
                # choose frontier and plan to it
                frontier = self.choose_frontier()
                if frontier is None:
                    # nowhere to explore
                    return False
                plan = self.plan_to(frontier)
                if plan:
                    self.current_plan = plan
                else:
                    return False

        # Follow plan one step
        if len(self.current_plan) >= 2:
            next_pos = self.current_plan[1]
            # if next_pos became a known wall in the meantime, replan
            if next_pos in self.known_walls:
                self.metrics.replans += 1
                self.current_plan = []
                return True
            # move
            self.current = next_pos
            self.metrics.steps += 1
            self.metrics.path_taken.append(self.current)
            # drop the executed step from plan
            self.current_plan = self.current_plan[1:]
            # perceive again after moving
            if not self.full_map:
                self._reveal_from(self.current)
            return True

        # plan exhausted but didn't reach goal
        self.current_plan = []
        return True

    def run(self, max_steps: int = 10000) -> Metrics:
        start_time = time.time()
        steps = 0
        while steps < max_steps:
            cont = self.step()
            if not cont:
                break
            steps += 1
        # finalize metrics
        self.metrics.steps = steps
        self.metrics.reached_goal = (self.current == self.goal)
        return self.metrics


def demo():
    repo_root = Path(__file__).resolve().parents[2]
    demo_map = repo_root / "maps" / "demo.csv"
    agent = OnlineAgent(demo_map, full_map=False, search_algo=astar)
    metrics = agent.run(1000)
    print(metrics)


if __name__ == "__main__":
    demo()
