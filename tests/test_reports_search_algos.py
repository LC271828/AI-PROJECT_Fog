"""Report-style tests for search algorithms that log useful context when they pass.

These tests validate correctness and also log the algorithm, path length,
path itself, and (when available) basic stats like nodes expanded and runtime.
"""

import logging
import pytest


try:
    import src.search as S
except Exception as e:  # pragma: no cover
    pytest.skip(f"Cannot import src.search: {e}")


def _grid_neighbors(width: int, height: int, walls: set[tuple[int, int]]):
    walls = set(walls)

    def neighbors(rc: tuple[int, int]):
        r, c = rc
        for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < height and 0 <= nc < width and (nr, nc) not in walls:
                yield (nr, nc)

    return neighbors


@pytest.mark.parametrize("algo", ["bfs", "ucs", "astar"])  # DFS not optimal; skip here
def test_search_algorithms_on_open_3x3_log_report(algo):
    """Expect shortest path length 4 from (0,0) to (2,2) on an open 3x3 grid."""
    logger = logging.getLogger(__name__)

    neighbors = _grid_neighbors(3, 3, walls=set())
    start, goal = (0, 0), (2, 2)

    path = S.ALGORITHMS_NEIGHBORS[algo](start, goal, neighbors)
    logger.info("[search] algo=%s path_len=%d path=%s", algo, len(path) - 1 if path else -1, path)

    # Validate
    assert path and path[0] == start and path[-1] == goal
    assert len(path) - 1 == 4

    # If stats wrappers exist, log them as well
    if hasattr(S, "ALGORITHMS_NEIGHBORS_WITH_STATS"):
        res = S.ALGORITHMS_NEIGHBORS_WITH_STATS[algo](start, goal, neighbors)
        logger.info(
            "[search] stats algo=%s nodes=%d runtime=%.6fs cost=%d",
            algo,
            getattr(res, "nodes_expanded", -1),
            getattr(res, "runtime", -1.0),
            getattr(res, "cost", -1),
        )


def test_blocked_goal_logs_empty_path():
    """When the goal is boxed in by walls, expect an empty path (no route)."""
    logger = logging.getLogger(__name__)
    walls = {(0, 1), (1, 0)}  # block off the goal at (1,1) from (0,0)
    neighbors = _grid_neighbors(2, 2, walls=walls)

    start, goal = (0, 0), (1, 1)
    path_astar = S.astar_neighbors(start, goal, neighbors)
    path_bfs = S.bfs_neighbors(start, goal, neighbors)

    logger.info("[search] blocked paths astar=%s bfs=%s", path_astar, path_bfs)

    assert path_astar == []
    assert path_bfs == []
