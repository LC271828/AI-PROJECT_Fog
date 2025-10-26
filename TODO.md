# Project TODOs

<!-- CHANGE (2025-10-25): Updated to reflect current completion status. Grid/Search/Agent are in place; CLI/Visualize pending. -->

Core modules
- [x] src/grid.py: Grid dataclass, strict CSV loader (classmethod from_csv), in_bounds, passable, neighbors4, fog helpers
- [x] src/search.py: bfs_neighbors/dfs_neighbors/ucs_neighbors/astar_neighbors, reconstruct, ALGORITHMS_NEIGHBORS, with-stats wrappers
- [x] src/agent.py: Metrics dataclass, OnlineAgent with step()/run(), basic frontier exploration
- [x] src/main.py: CLI wiring (load_config, parse args, run headless; --with-stats supported)
- [ ] src/visualize.py (optional): pygame renderer and loop

Maps
- [x] Add small edge-case maps for testing (boxed_start, corridors, dead_end_maze, open_room)

Tests
- [x] tests/test_search.py: unit tests for neighbor-function BFS/DFS/UCS/A*
- [x] tests/test_fog*.py: radius-one reveal, walls visibility, no re-fogging
- [x] tests/test_grid_oob.py: explicit False on out-of-bounds for is_wall/passable
- [x] tests/test_visualize_text*.py: text overlay basics
- [x] API contract smoke: tests/test_team_api_grid.py and tests/test_team_api_agent.py
- [x] Rich summary plugin and per-test banners for informative output

Docs
- [ ] docs/assignment_summary.md: Fill in project summary
- [ ] docs/whatsapp_digest.md: Summarize decisions and roles from chat
- [x] docs/decisions.md: Record design choices as they solidify (kept up-to-date)
- [x] docs/PEAS.md: Added PEAS summary
- [x] TEAM_API.md and README.md: aligned with current API

Tooling
- [x] requirements.txt: pytest pinned; rich plugin support; pygame optional via setup flag
- [ ] .vscode/settings.json: enable pytest discovery (optional)

Nice-to-have
- [ ] scripts/bench.py: benchmark harness once core modules exist
