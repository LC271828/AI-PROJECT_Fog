from pathlib import Path
from experiments.ahsan.agent import OnlineAgent
from experiments.ahsan import search
from experiments.asthar.grid import Grid


def test_agent_full_map_reaches_goal():
    repo_root = Path(__file__).resolve().parents[2]
    demo_map = repo_root / "maps" / "demo.csv"
    g = Grid(map=demo_map)
    algo = search.ALGORITHMS_WITH_STATS.get("astar", search.astar_with_stats)
    agent = OnlineAgent(g, full_map=True, search_algo=algo)
    metrics = agent.run(1000)
    assert metrics.reached_goal is True
    assert hasattr(metrics, "nodes_expanded")
    assert hasattr(metrics, "runtime")
    assert isinstance(metrics.nodes_expanded, int)


def test_agent_fog_mode_metrics_present():
    repo_root = Path(__file__).resolve().parents[2]
    demo_map = repo_root / "maps" / "demo.csv"
    g = Grid(map=demo_map)
    algo = search.ALGORITHMS_WITH_STATS.get("astar", search.astar_with_stats)
    agent = OnlineAgent(g, full_map=False, search_algo=algo)
    metrics = agent.run(500)
    # We may or may not reach the goal depending on map/implementation; just assert metrics fields
    assert hasattr(metrics, "nodes_expanded")
    assert hasattr(metrics, "runtime")
    assert isinstance(metrics.nodes_expanded, int)
