"""Agent fog progression tests.

Purpose:
- Ensure that under fog, visibility never shrinks (no re-fogging) and typically grows
    as the agent steps.
- Sanity-check that the agent's recorded path length matches its step counter.
"""
from pathlib import Path

from src.grid import Grid
from src.agent import OnlineAgent
from src.search import ALGORITHMS_NEIGHBORS as SEARCH_ALGOS


def test_agent_reveals_more_over_time_under_fog():
    """Stepping a few times under fog should monotonically increase visibility."""
    repo_root = Path(__file__).resolve().parents[1]
    demo_map = repo_root / "maps" / "demo.csv"

    g = Grid.from_csv(demo_map)
    # Use BFS for deterministic behavior
    agent = OnlineAgent(g, full_map=False, search_algo=SEARCH_ALGOS["bfs"])

    # After initialization, start should be visible, maybe neighbors too depending on init
    initial_visible = set(g.visible_tiles())
    assert (g.start in initial_visible)

    # Step a few times; visibility should not shrink and typically should grow
    for _ in range(5):
        cont = agent.step()
        # break if finished
        if not cont:
            break
    after_visible = set(g.visible_tiles())

    # Fog has no re-fogging: visibility is monotonic non-decreasing
    assert initial_visible.issubset(after_visible)

    # Either we revealed more or finished quickly; both acceptable; ensure path_taken length equals steps
    assert len(agent.metrics.path_taken) == agent.metrics.steps + 1  # includes start
