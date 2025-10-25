from pathlib import Path

import pytest


def test_reveal_from_start_radius_one():
	# Load grid
	repo_root = Path(__file__).resolve().parents[1]
	demo_map = repo_root / "maps" / "demo.csv"
	from src.grid import Grid

	g = Grid.from_csv(demo_map)

	# Initially no tiles are visible
	assert all(all(not cell for cell in row) for row in g.visible)

	# Reveal from start
	revealed = g.reveal_from(g.start)
	# Start must be visible
	sr, sc = g.start
	assert g.visible[sr][sc] is True
	# All revealed are in-bounds
	assert all(g.in_bounds(r, c) for r, c in revealed)
	# Radius one means at most 1 step in U/R/D/L plus self
	assert len(revealed) <= 5
	# Visible tiles should include start
	assert (sr, sc) in g.visible_tiles()
