import inspect
from pathlib import Path

import pytest


def _load_grid():
    from src.grid import Grid
    demo = Path(__file__).resolve().parents[1] / "maps" / "demo.csv"
    # Prefer TEAM_API classmethod constructor first
    try:
        g2 = Grid.from_csv(demo)
        return g2
    except Exception:
        pass
    # Fall back to instance-style (compatible with experimental implementation)
    try:
        g = Grid()
        if hasattr(g, "from_csv") and callable(getattr(g, "from_csv")):
            try:
                getattr(g, "from_csv")(demo)
                return g
            except Exception:
                pass
        if hasattr(g, "_from_csv") and callable(getattr(g, "_from_csv")):
            getattr(g, "_from_csv")(demo)
            return g
    except Exception:
        pass
    pytest.fail("Could not construct Grid via classmethod or instance from_csv; expected API-compatible implementation")


def test_grid_api_contract_fields_and_methods():
    from src.grid import Grid

    # class exists
    assert inspect.isclass(Grid)

    g = _load_grid()

    # Required fields
    assert isinstance(g.start, tuple) and len(g.start) == 2
    assert isinstance(g.goal, tuple) and len(g.goal) == 2
    assert isinstance(g.width, int) and g.width > 0
    assert isinstance(g.height, int) and g.height > 0
    assert isinstance(g.grid, list)
    assert isinstance(g.visible, list)
    # visible shape matches grid dimensions (best-effort check)
    assert len(g.visible) == g.height
    if g.height:
        assert all(isinstance(row, list) for row in g.visible)

    # Required methods present and callable
    for name in (
        "in_bounds",
        "is_wall",
        "passable",
        "neighbors4",
        "tile_at",
        "is_visible",
        "reveal_from",
        "get_visible_neighbors",
        "visible_tiles",
    ):
        assert hasattr(g, name), f"Grid missing method {name}"
        assert callable(getattr(g, name)), f"Grid.{name} is not callable"
