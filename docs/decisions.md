Architectural decisions:
- Separation of concerns: grid/search/agent/visualize
- Headless-first design; GUI optional
- CSV maps for version control
- Online agent with frontier exploration when goal is unknown/unreachable on known map

2025-10-23 — Search API choice
- Canonical search is neighbor-function based (bfs_neighbors/ucs_neighbors/dfs_neighbors/astar_neighbors).
- Reason: matches experiments, works best with fog (plan on visible subgraph), easy to test and collect metrics.
- Optional offline baseline wrappers may use `grid.neighbors4`, but are not part of the main contract.

Project-wide conventions:
- Movement: up/down/left/right only (no diagonals)
- Fog: radius 1; walls visible when adjacent and block reveal beyond; no re-fogging
- Heuristic: Manhattan for A*
- Re-planning: Agent re-runs search as visibility expands
- Branch workflow: main (final) and dev (integration)
