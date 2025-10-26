"""Fog visibility rule tests.

Purpose:
- Adjacent walls become visible but remain impassable and excluded from visible neighbors.
- Visible neighbors are both visible and passable.
- Visibility is persistent (no re-fogging when revealing again).
"""
from pathlib import Path

from src.grid import Grid


def test_walls_become_visible_but_not_passable():
    """Walls next to the start should appear in visibility but not be passable or neighbor candidates."""
    repo_root = Path(__file__).resolve().parents[1]
    demo_map = repo_root / "maps" / "demo.csv"
    g = Grid.from_csv(demo_map)

    # Initially all hidden
    assert all(not any(row) for row in g.visible)

    # Reveal from start
    sr, sc = g.start
    revealed = g.reveal_from(g.start)
    assert (sr, sc) in revealed

    # Any adjacent walls should be visible but not included as passable or visible neighbors
    for (r, c) in g.neighbors4(sr, sc):
        if g.tile_at(r, c) == "1":
            assert g.is_visible(r, c) is True
            assert g.passable(r, c) is False
            assert (r, c) not in g.get_visible_neighbors(g.start)


def test_visible_neighbors_only_visible_and_passable():
    """After reveal, all visible neighbors returned must also be passable."""
    repo_root = Path(__file__).resolve().parents[1]
    demo_map = repo_root / "maps" / "demo.csv"
    g = Grid.from_csv(demo_map)

    # Before revealing, neighbors shouldn't be considered visible
    sr, sc = g.start
    nb_before = g.get_visible_neighbors((sr, sc))
    assert nb_before == []

    # After revealing from start, passable visible neighbors appear
    g.reveal_from((sr, sc))
    nb_after = g.get_visible_neighbors((sr, sc))
    for (r, c) in nb_after:
        assert g.is_visible(r, c)
        assert g.passable(r, c)


def test_no_refogging_cells_stay_visible():
    """Revealing again never hides previously visible tiles (no re-fogging)."""
    repo_root = Path(__file__).resolve().parents[1]
    demo_map = repo_root / "maps" / "demo.csv"
    g = Grid.from_csv(demo_map)

    sr, sc = g.start
    g.reveal_from((sr, sc))
    vis1 = set(g.visible_tiles())

    # Reveal again from another visible neighbor (if any), then ensure previous remain visible
    nb = g.get_visible_neighbors((sr, sc))
    if nb:
        g.reveal_from(nb[0])
    vis2 = set(g.visible_tiles())
    assert vis1.issubset(vis2)
