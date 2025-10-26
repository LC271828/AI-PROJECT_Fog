"""Matrix tests comparing offline shortest paths to agent runs without fog.

We verify that, for unit-cost maps, BFS/UCS/A* produce optimal paths offline,
then ensure the OnlineAgent with full_map=True achieves the same cost.
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
    "maps/demo2.csv",
    "maps/open_room.csv",
]
ALGOS = ["bfs", "ucs", "astar"]  # DFS is not optimal by design


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
@pytest.mark.parametrize("algo", ALGOS)
def test_offline_cost_equals_agent_no_fog_cost(map_rel, algo):
    """For BFS/UCS/A*, agent(no-fog) should match the offline optimal cost on these maps."""
    logger = logging.getLogger(__name__)
    repo_root = Path(__file__).resolve().parents[1]

    g = Grid.from_csv(repo_root / map_rel)

    # Offline shortest path with the selected algorithm
    neighbors = _full_neighbors(g)
    path = S.ALGORITHMS_NEIGHBORS[algo](g.start, g.goal, neighbors)
    assert path, f"offline path not found for {map_rel}"
    offline_cost = len(path) - 1

    # Agent in no-fog mode (full_map=True)
    agent = OnlineAgent(g, full_map=True, search_algo=S.ALGORITHMS_NEIGHBORS[algo])
    m = agent.run(max_steps=offline_cost + 100)

    logger.info(
        "[matrix] map=%s algo=%s offline_cost=%d agent_cost=%d steps=%d replans=%d reached=%s",
        map_rel,
        algo,
        offline_cost,
        m.cost,
        m.steps,
        m.replans,
        m.reached_goal,
    )

    assert m.reached_goal is True
    assert m.cost == offline_cost
