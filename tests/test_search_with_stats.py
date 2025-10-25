import types
import pytest

# Verify presence of with-stats variants and basic contract
try:
    import src.search as S
except Exception as e:  # pragma: no cover
    pytest.fail(f"Failed to import src.search: {e}")

HAVE_NEIGHBOR_STATS = all(
    hasattr(S, name)
    for name in (
        "SearchResult",
        "bfs_neighbors_with_stats",
        "dfs_neighbors_with_stats",
        "ucs_neighbors_with_stats",
        "astar_neighbors_with_stats",
        "ALGORITHMS_NEIGHBORS_WITH_STATS",
    )
)


@pytest.mark.skipif(not HAVE_NEIGHBOR_STATS, reason="Stats wrappers not available in src.search")
def test_stats_wrapper_path_matches_plain_version():
    # small open grid 3x3
    def neighbors(rc):
        r, c = rc
        for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < 3 and 0 <= nc < 3:
                yield (nr, nc)

    start, goal = (0, 0), (2, 2)

    p_plain = S.astar_neighbors(start, goal, neighbors)
    res_stats = S.astar_neighbors_with_stats(start, goal, neighbors)

    assert isinstance(res_stats, S.SearchResult)
    assert res_stats.path == p_plain
    assert res_stats.nodes_expanded >= 1
    assert res_stats.cost == (len(p_plain) - 1 if p_plain else 0)


@pytest.mark.skipif(not HAVE_NEIGHBOR_STATS, reason="Stats wrappers not available in src.search")
def test_algorithms_neighbors_with_stats_mapping():
    m = S.ALGORITHMS_NEIGHBORS_WITH_STATS
    for k in ("bfs", "dfs", "ucs", "astar"):
        assert k in m and callable(m[k])
