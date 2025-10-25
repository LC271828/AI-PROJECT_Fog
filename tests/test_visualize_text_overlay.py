"""Text visualization plan overlay tests.

Purpose:
- Ensure the plan overlay draws a marker on a visible, passable neighbor and
    respects base symbols (does not overwrite S/G/@).
"""
from pathlib import Path

from examples.visualize_text import render_masked
from src.grid import Grid


def test_plan_overlay_draws_star_on_visible_free_cell():
    """Overlay should include '*' on a visible, passable neighbor from start."""
    repo_root = Path(__file__).resolve().parents[1]
    demo_map = repo_root / "maps" / "demo.csv"
    g = Grid.from_csv(demo_map)

    # Reveal from start so adjacent free becomes visible
    g.reveal_from(g.start)

    sr, sc = g.start
    # pick any visible neighbor that is passable to overlay '*'
    cand = None
    for (r, c) in g.neighbors4(sr, sc):
        if g.is_visible(r, c) and g.passable(r, c):
            cand = (r, c)
            break
    assert cand is not None, "expected at least one visible passable neighbor next to start"

    # Render with a fake short plan start -> cand
    masked = render_masked(g, agent_pos=g.start, plan=[g.start, cand])

    # The overlay avoids overwriting '@', 'S', 'G'; cand is free so star should appear
    assert "*" in masked
