"""Grid helpers out-of-bounds behavior.

Purpose:
- Ensure helper methods return explicit False when coordinates are outside the grid.
"""
from pathlib import Path


def test_grid_oob_helpers_return_false():
    """is_wall/passable should return False on out-of-bounds coordinates."""
    from src.grid import Grid
    repo_root = Path(__file__).resolve().parents[1]
    demo_map = repo_root / "maps" / "demo.csv"

    g = Grid.from_csv(demo_map)

    # Pick out-of-bounds positions
    oobs = [(-1, 0), (0, -1), (g.height, 0), (0, g.width)]

    for r, c in oobs:
        assert g.is_wall(r, c) is False
        assert g.passable(r, c) is False
