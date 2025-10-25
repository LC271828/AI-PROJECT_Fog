"""TEAM_API contract test for the Agent.

Purpose:
- Verify that OnlineAgent and Metrics exist and that run() returns a Metrics-like object
    with the expected fields after a short execution.
"""
from pathlib import Path
import types

import pytest


def test_agent_api_contract_exists_and_runs():
    """Ensure agent and metrics classes exist and are minimally functional."""
    # Import OnlineAgent and Metrics
    import src.agent as A
    assert hasattr(A, "OnlineAgent"), "src.agent.OnlineAgent missing"
    assert hasattr(A, "Metrics"), "src.agent.Metrics missing"

    from src.grid import Grid
    demo = Path(__file__).resolve().parents[1] / "maps" / "demo.csv"
    # build grid via instance-style from_csv (compatible with current implementation)
    g = Grid.from_csv(demo)

    # construct agent, ensure methods exist
    agent = A.OnlineAgent(g, full_map=False)
    assert hasattr(agent, "step") and callable(agent.step)
    assert hasattr(agent, "run") and callable(agent.run)

    # run a few steps, ensure Metrics-like object returned
    m = agent.run(max_steps=5)
    assert isinstance(m, A.Metrics)
    for field in ("steps", "replans", "runtime", "cost", "reached_goal", "path_taken"):
        assert hasattr(m, field), f"Metrics missing field {field}"
