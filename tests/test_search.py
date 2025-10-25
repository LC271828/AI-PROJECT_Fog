"""Search API contract and correctness tests.

Purpose:
- Validate presence of the neighbor-function API and its mapping.
- Check A* shortest path on an open grid and equality of UCS/BFS on unit costs.
- Ensure blocked goals return empty paths.
"""
import types
import pytest


# Contract: neighbor-function API should live in src.search
try:
	import src.search as S
except Exception as e:  # pragma: no cover
	pytest.fail(f"Failed to import src.search: {e}")


HAVE_NEIGHBOR_API = all(
	hasattr(S, name)
	for name in (
		"bfs_neighbors",
		"dfs_neighbors",
		"ucs_neighbors",
		"astar_neighbors",
		"ALGORITHMS_NEIGHBORS",
	)
)


@pytest.mark.skipif(not HAVE_NEIGHBOR_API, reason="Neighbor-function API not implemented yet in src.search (see TEAM_API.md)")
def test_neighbor_api_contract_exists():
	"""Module should expose bfs/dfs/ucs/astar functions and ALGORITHMS_NEIGHBORS mapping."""
	# Functions are callable
	assert isinstance(S.bfs_neighbors, types.FunctionType)
	assert isinstance(S.dfs_neighbors, types.FunctionType)
	assert isinstance(S.ucs_neighbors, types.FunctionType)
	assert isinstance(S.astar_neighbors, types.FunctionType)
	# Mapping exists and contains the algorithms (including greedy)
	algos = S.ALGORITHMS_NEIGHBORS
	assert set(algos.keys()) == {"bfs", "dfs", "ucs", "astar", "greedy"}


def _grid_neighbors(width: int, height: int, walls: set[tuple[int, int]]):
	walls = set(walls)
	def neighbors(rc: tuple[int, int]):
		r, c = rc
		for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
			nr, nc = r + dr, c + dc
			if 0 <= nr < height and 0 <= nc < width and (nr, nc) not in walls:
				yield (nr, nc)
	return neighbors


@pytest.mark.skipif(not HAVE_NEIGHBOR_API, reason="Neighbor-function API not implemented yet in src.search (see TEAM_API.md)")
def test_astar_neighbors_finds_shortest_path_on_open_grid():
	n = _grid_neighbors(3, 3, walls=set())
	start, goal = (0, 0), (2, 2)
	"""A* should find the length-4 shortest path on a 3x3 open grid (corner to corner)."""
	path = S.astar_neighbors(start, goal, n, h=getattr(S, "manhattan", lambda a, b: abs(a[0]-b[0]) + abs(a[1]-b[1])))
	assert path[0] == start and path[-1] == goal
	assert len(path) - 1 == 4  # shortest path length in a 3x3 from corner to corner


@pytest.mark.skipif(not HAVE_NEIGHBOR_API, reason="Neighbor-function API not implemented yet in src.search (see TEAM_API.md)")
def test_ucs_equals_bfs_on_unit_costs():
	"""On unit-cost graphs, UCS and BFS should yield paths of equal cost."""
	walls = {(1, 1)}
	n = _grid_neighbors(3, 3, walls=walls)
	start, goal = (0, 0), (2, 2)
	p_bfs = S.bfs_neighbors(start, goal, n)
	p_ucs = S.ucs_neighbors(start, goal, n)
	assert (len(p_bfs) - 1) == (len(p_ucs) - 1)


@pytest.mark.skipif(not HAVE_NEIGHBOR_API, reason="Neighbor-function API not implemented yet in src.search (see TEAM_API.md)")
def test_blocked_goal_returns_empty():
	"""When the goal is blocked off, search functions should return an empty path."""
	walls = {(0, 1), (1, 0)}  # block off the goal at (1,1) from (0,0)
	n = _grid_neighbors(2, 2, walls=walls)
	assert S.bfs_neighbors((0, 0), (1, 1), n) == []
	assert S.astar_neighbors((0, 0), (1, 1), n) == []
