"""Report-style tests for the OnlineAgent that log steps, cost, and outcome.

These are smoke-level checks with informative output to make passing runs
explain what happened (fog vs no-fog, algorithm used, metrics observed).
"""

import logging
from pathlib import Path

import pytest


@pytest.mark.parametrize(
    "algo, no_fog, max_steps",
    [
        ("bfs", False, 30),  # fogged BFS small step budget
        ("astar", True, 50),  # no-fog A*
    ],
)
def test_agent_runs_and_reports_metrics_on_demo(algo, no_fog, max_steps):
    """Run the agent briefly on demo.csv and log key metrics and constraints."""
    logger = logging.getLogger(__name__)

    from src.grid import Grid
    from src.agent import OnlineAgent
    from src.search import ALGORITHMS_NEIGHBORS as SEARCH_ALGOS

    repo_root = Path(__file__).resolve().parents[1]
    demo_map = repo_root / "maps" / "demo.csv"

    g = Grid.from_csv(demo_map)
    agent = OnlineAgent(g, full_map=no_fog, search_algo=SEARCH_ALGOS[algo])

    m = agent.run(max_steps=max_steps)

    logger.info(
        "[agent] algo=%s fog=%s steps=%d cost=%d replans=%d reached=%s path_len=%d",
        algo,
        not no_fog,
        m.steps,
        m.cost,
        m.replans,
        m.reached_goal,
        len(m.path_taken) - 1,
    )

    # Basic shape assertions
    assert m.steps >= 0 and m.cost >= 0
    assert len(m.path_taken) == m.steps + 1
    # We don't require reaching the goal under fog with small budgets; just ensure no errors occurred
