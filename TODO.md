# Project TODOs

<!-- CHANGE (2025-10-25): Updated to reflect current completion status. Grid/Search/Agent are in place; CLI/Visualize pending. -->

Core modules
- [x] src/grid.py: Grid dataclass, strict CSV loader (classmethod from_csv), in_bounds, passable, neighbors4, fog helpers
- [x] src/search.py: bfs_neighbors/dfs_neighbors/ucs_neighbors/astar_neighbors, reconstruct, ALGORITHMS_NEIGHBORS
- [x] src/agent.py: Metrics dataclass, OnlineAgent with step()/run(), basic frontier exploration
- [ ] src/main.py: CLI wiring (load_config, parse args, run headless/GUI)
- [ ] src/visualize.py (optional): pygame renderer and loop

Maps
- [ ] Add 1-2 more small maps to maps/ for testing (maps/demo2.csv exists; consider adding one more)

Tests
- [x] tests/test_search.py: unit tests for neighbor-function BFS/DFS/UCS/A*
- [x] tests/test_fog.py: basic radius-one reveal test (add wall-block/persistence cases later)
- [x] API contract smoke: tests/test_team_api_grid.py and tests/test_team_api_agent.py

Docs
- [ ] docs/assignment_summary.md: Fill in project summary
- [ ] docs/whatsapp_digest.md: Summarize decisions and roles from chat
- [x] docs/decisions.md: Record design choices as they solidify (kept up-to-date)
- [x] docs/PEAS.md: Added PEAS summary
- [x] TEAM_API.md and README.md: aligned with current API

Tooling
- [x] requirements.txt: pytest pinned; pygame optional via setup flag
- [ ] .vscode/settings.json: enable pytest discovery (optional)

Nice-to-have
- [ ] scripts/bench.py: benchmark harness once core modules exist
