"""Online agent (TODO).

Planned responsibilities:
- Maintain internal knowledge: seen cells, known free cells.
- Perceive (update visibility), Plan (choose path with selected search), Act (move one step).
- Metrics tracking (steps, replans), path_taken list.

Next steps:
- Define Metrics dataclass.
- Implement OnlineAgent with step() and run() methods.
- Implement exploration strategy when goal path is unknown (frontier-based).
"""

# TODO: implement Metrics and OnlineAgent as per description above.

from __future__ import annotations

# ===== Begin copied implementation from experiments/ahsan/agent.py (verbatim) =====
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
# from __future__ import annotations  # already declared at top of file

from dataclasses import dataclass, field
from typing import Callable, Iterable, List, Tuple, Set, Optional, Any
from pathlib import Path
import time

# helper: ensure coords are canonical tuples
from typing import Sequence


def normalize_coord(pos: Sequence[int]) -> Tuple[int, int]:
	"""Return a canonical (row, col) tuple from a 2-item sequence.

	Raises
	- ValueError: if ``pos`` is not a 2-length sequence of ints.
	"""
	if isinstance(pos, tuple):
		if len(pos) != 2:
			raise ValueError("coord must be length 2")
		return pos
	if not isinstance(pos, (list, tuple)):
		raise ValueError("coord must be a sequence of two ints")
	if len(pos) != 2:
		raise ValueError("coord must be length 2")
	r, c = pos
	return (int(r), int(c))

from src.search import bfs_neighbors as bfs, astar_neighbors as astar

Coord = Tuple[int, int]


@dataclass
class Metrics:
	"""Run statistics collected by the online agent.

	Fields
	- start, goal: coordinates
	- steps: count of moves executed
	- nodes_expanded: optional count reported by search (if available)
	- replans: number of times a plan was discarded due to a newly-known obstacle
	- runtime: total runtime accumulated/observed (seconds)
	- cost: path cost on unit-cost maps (len(path_taken) - 1)
	- reached_goal: terminal success flag
	- path_taken: sequence of visited coordinates including start
	"""
	# TEAM_API fields + extras
	start: Coord
	goal: Coord
	steps: int = 0
	nodes_expanded: int = 0
	replans: int = 0
	runtime: float = 0.0
	cost: int = 0
	reached_goal: bool = False
	path_taken: List[Coord] = field(default_factory=list)

	def __post_init__(self):
		if not self.path_taken:
			self.path_taken = [self.start]


class OnlineAgent:
	"""Simple online agent that perceives, plans, and acts under fog or full map.

	The agent keeps sets of known passable cells and walls. Under fog, it delegates
	perception to ``Grid.reveal_from`` each step. Planning uses a provided search
	function over an appropriate neighbor function depending on fog state.
	"""
	def __init__(self, grid, full_map: bool = True, search_algo: Optional[Callable] = None):
		"""
		grid: a Grid instance (constructed externally). The Grid must implement
		the TEAM_API: attributes `start`, `goal`, `height`, `width`, and methods
		`reveal_from(pos)` and `get_visible_neighbors(pos)`.

		The agent no longer attempts to construct a Grid from a path — callers
		must pass a ready Grid instance. This keeps the agent robust and avoids
		import/constructor fragility during transitions.
		"""
		# Don't accept raw path-like values here; require a Grid instance.
		if isinstance(grid, Path):
			raise TypeError("OnlineAgent now requires a Grid instance; construct a Grid (e.g. src.grid.Grid.from_csv(path)) and pass it in.")
		self.impl = grid
		# default to A* if no search algo provided
		self.search = search_algo or astar
		# normalize start/goal to tuples
		self.start: Coord = normalize_coord(tuple(self.impl.start))
		self.goal: Coord = normalize_coord(tuple(self.impl.goal))
		self.current: Coord = self.start
		self.full_map = full_map

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
			# CHANGE(TEAM_API): rely solely on Grid.reveal_from for perception
			if not hasattr(self.impl, "reveal_from"):
				raise TypeError("Grid implementation must provide reveal_from(pos) per TEAM_API")
			newly = self.impl.reveal_from(self.start)
			for p in newly:
				p = normalize_coord(p)
				tile = self._tile_at(p)
				if tile == '1':
					self.known_walls.add(p)
				else:
					self.known_passable.add(p)

		self.metrics = Metrics(start=self.start, goal=self.goal)
		self.current_plan: List[Coord] = []

	# --- perception helpers (experimental wrappers around Grid) ---
	def _in_bounds(self, pos: Coord) -> bool:
		"""Internal bounds check against the underlying grid dimensions."""
		r, c = pos
		return 0 <= r < self.impl.height and 0 <= c < self.impl.width

	def _tile_at(self, pos: Coord) -> str:
		"""Internal accessor for raw map symbol at a coordinate."""
		r, c = pos
		return self.impl.grid[r][c]

    # NOTE: Internal _reveal_from removed; agent now delegates to Grid.reveal_from exclusively.

	# --- neighbor function used by search algorithms ---
	def known_neighbors(self, pos: Coord) -> Iterable[Coord]:
		"""Neighbors within the agent's current known passable set.

		Order is deterministic: Up, Right, Down, Left.
		"""
		# deterministic neighbor order: Up, Right, Down, Left
		for dr, dc in [(-1, 0), (0, 1), (1, 0), (0, -1)]:
			n = (pos[0] + dr, pos[1] + dc)
			if n in self.known_passable:
				yield n

	# --- planning/execution ---
	def plan_to(self, target: Coord) -> List[Coord]:
		"""Compute a path from current position to ``target`` using the configured search.

		Chooses an appropriate neighbor function based on fog state:
		- full_map: authoritative grid neighbors filtered by passable
		- fogged: grid.get_visible_neighbors
		- fallback: agent's known graph
		"""
		# CHANGE(TEAM_API): When full_map is True, use authoritative grid neighbors (no fog).
		# Otherwise, prefer impl.get_visible_neighbors under fog. Fallback to agent-known.
		if self.full_map and hasattr(self.impl, "neighbors4"):
			# Only return passable neighbors in full-map mode
			neighbor_fn = lambda p: [n for n in self.impl.neighbors4(p[0], p[1]) if self.impl.passable(n[0], n[1])]
		elif hasattr(self.impl, "get_visible_neighbors"):
			neighbor_fn = lambda p: self.impl.get_visible_neighbors(p)
		else:
			neighbor_fn = lambda p: self.known_neighbors(p)

		res = self.search(self.current, target, neighbor_fn)
		# Search may return either a Path or a SearchResult-like object with .path
		res_any: Any = res
		if hasattr(res_any, "path"):
			path = res_any.path
			self.metrics.nodes_expanded += getattr(res_any, "nodes_expanded", 0)
			self.metrics.runtime += getattr(res_any, "runtime", 0.0)
			self.metrics.cost = getattr(res_any, "cost", self.metrics.cost)
		else:
			path = res_any
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
			# CHANGE(TEAM_API): Use Grid.reveal_from each step
			if not hasattr(self.impl, "reveal_from"):
				raise TypeError("Grid implementation must provide reveal_from(pos) per TEAM_API")
			newly = self.impl.reveal_from(self.current)
			for p in newly:
				p = normalize_coord(p)
				tile = self._tile_at(p)
				if tile == '1':
					self.known_walls.add(p)
				else:
					self.known_passable.add(p)

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
				# CHANGE(TEAM_API): Use Grid.reveal_from after moving as well
				if not hasattr(self.impl, "reveal_from"):
					raise TypeError("Grid implementation must provide reveal_from(pos) per TEAM_API")
				newly = self.impl.reveal_from(self.current)
				for p in newly:
					p = normalize_coord(p)
					tile = self._tile_at(p)
					if tile == '1':
						self.known_walls.add(p)
					else:
						self.known_passable.add(p)
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
		# CHANGE(METRICS): Preserve movement-based steps tracked in step(); do not overwrite
		# with iteration count. This keeps 'steps' equal to actual moves executed.
		self.metrics.reached_goal = (self.current == self.goal)
		# CHANGE(METRICS): Provide a simple cost based on the taken path length on unit-cost maps.
		if self.metrics.path_taken:
			self.metrics.cost = max(0, len(self.metrics.path_taken) - 1)
		# CHANGE(METRICS): If no per-search runtime was accumulated, set total runtime.
		if not self.metrics.runtime:
			self.metrics.runtime = max(0.0, time.time() - start_time)
		return self.metrics


# (Demo code removed from src; see scripts/demo_agent.py for a runnable demo.)
# ===== End copied implementation from experiments/ahsan/agent.py =====
