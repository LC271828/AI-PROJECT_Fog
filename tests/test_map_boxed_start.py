"""Tests for maps/boxed_start.csv behaviour under offline search and agent runs.

Expectations:
- Offline search on full map finds no path (blocked by walls).
- Agent with no fog (full map) detects no path and stops without moving.
- Agent under fog reveals walls, finds no frontier, and stops without moving.
"""
from __future__ import annotations

import logging
from pathlib import Path

import pytest


def _load():
    from src.grid import Grid
    repo_root = Path(__file__).resolve().parents[1]
    return Grid.from_csv(repo_root / "maps" / "boxed_start.csv")


def _full_neighbors(g):
    def neighbors(rc):
        r, c = rc
        out = []
        for (nr, nc) in g.neighbors4(r, c):
            if g.passable(nr, nc):
                out.append((nr, nc))
        return out
    return neighbors


def test_offline_search_finds_no_path_boxed_start():
    import src.search as S
    g = _load()
    n = _full_neighbors(g)
    for algo in ("bfs", "ucs", "astar", "dfs"):
        path = S.ALGORITHMS_NEIGHBORS[algo](g.start, g.goal, n)
        assert path == [], f"expected no path with {algo} on boxed_start"


def test_agent_no_fog_stops_immediately_boxed_start():
    import src.search as S
    from src.agent import OnlineAgent

    g = _load()
    agent = OnlineAgent(g, full_map=True, search_algo=S.ALGORITHMS_NEIGHBORS["bfs"])  # algo choice irrelevant here
    m = agent.run(max_steps=10)

    assert m.reached_goal is False
    assert m.steps == 0
    assert m.cost == 0


def test_agent_fog_stops_immediately_boxed_start():
    import src.search as S
    from src.agent import OnlineAgent

    g = _load()
    agent = OnlineAgent(g, full_map=False, search_algo=S.ALGORITHMS_NEIGHBORS["bfs"])  # fogged
    m = agent.run(max_steps=10)

    assert m.reached_goal is False
    assert m.steps == 0
    assert m.cost == 0
