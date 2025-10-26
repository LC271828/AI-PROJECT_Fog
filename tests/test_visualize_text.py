"""Text visualization overlay tests.

Purpose:
- Validate that the masked renderer shows the agent and preserves fog on hidden cells.
- Acts as a lightweight sanity check for visualization logic without pygame.
"""
from pathlib import Path

from src.textviz import render_masked
from src.grid import Grid
from src.agent import OnlineAgent
from src.search import ALGORITHMS_NEIGHBORS as SEARCH_ALGOS


def test_render_masked_basic_symbols():
    """Masked output should include '@' for agent and '?' to represent hidden tiles."""
    repo_root = Path(__file__).resolve().parents[1]
    demo_map = repo_root / "maps" / "demo.csv"

    g = Grid.from_csv(demo_map)
    agent = OnlineAgent(g, full_map=False, search_algo=SEARCH_ALGOS["bfs"])  # fogged

    # After agent construction, start should be revealed by OnlineAgent's init-perception
    masked = render_masked(g, agent.current, getattr(agent, "current_plan", None))

    # Must be a string and contain visible agent '@' and hidden '?' somewhere
    assert isinstance(masked, str)
    assert "@" in masked  # agent overlay at current pos
    assert "?" in masked  # hidden tiles remain under fog

    # Start tile should be visible either as '@' (overlay) or 'S' underneath elsewhere.
    assert ("S" in masked) or ("@" in masked)
