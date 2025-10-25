"""Fog vs Offline baseline tests.

We compute an offline shortest path cost via BFS on the full map as a baseline,
then run the OnlineAgent under fog and expect it to reach the goal within a
reasonable budget. We only assert reachability and that the cost is >= baseline.
"""
from __future__ import annotations

import logging
from pathlib import Path

import pytest

try:
    import src.search as S
    from src.grid import Grid
    from src.agent import OnlineAgent
except Exception as e:  # pragma: no cover
    pytest.skip(f"imports failed: {e}")


MAPS = [
    "maps/demo.csv",
    "maps/open_room.csv",
    "maps/dead_end_maze.csv",
]
ALGO = "bfs"  # deterministic and optimal on unit costs


def _full_neighbors(g: Grid):
    def neighbors(rc):
        r, c = rc
        out = []
        for (nr, nc) in g.neighbors4(r, c):
            if g.passable(nr, nc):
                out.append((nr, nc))
        return out
    return neighbors


@pytest.mark.parametrize("map_rel", MAPS, ids=lambda p: Path(p).stem)
def test_fog_agent_reaches_goal_within_budget(map_rel):
    """Under fog, agent should reach the goal within a generous budget.

    Budget strategy: baseline_cost * 5 + 50 (cap to a minimum of 100) to avoid flakiness.
    """
    logger = logging.getLogger(__name__)
    repo_root = Path(__file__).resolve().parents[1]

    g = Grid.from_csv(repo_root / map_rel)

    # Offline baseline via BFS on full map
    neighbors = _full_neighbors(g)
    baseline = S.ALGORITHMS_NEIGHBORS["bfs"](g.start, g.goal, neighbors)
    assert baseline, f"offline BFS found no path in {map_rel}"
    base_cost = len(baseline) - 1

    # Fogged agent with BFS
    agent = OnlineAgent(g, full_map=False, search_algo=S.ALGORITHMS_NEIGHBORS[ALGO])

    budget = max(100, base_cost * 5 + 50)
    m = agent.run(max_steps=budget)

    logger.info(
        "[fog] map=%s algo=%s base_cost=%d budget=%d steps=%d cost=%d replans=%d reached=%s",
        map_rel,
        ALGO,
        base_cost,
        budget,
        m.steps,
        m.cost,
        m.replans,
        m.reached_goal,
    )

    assert m.reached_goal is True
    assert m.cost >= base_cost
