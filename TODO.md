# Project TODOs (scaffold stage)

Core modules
- [ ] src/grid.py: Grid dataclass, from_csv, in_bounds, passable, neighbors (4-dir), visible(fog)
- [ ] src/search.py: bfs, dfs, ucs, astar, reconstruct, ALGORITHMS mapping
- [ ] src/agent.py: Metrics dataclass, OnlineAgent with step()/run(), frontier exploration
- [ ] src/main.py: CLI wiring (load_config, parse args, run headless/GUI)
- [ ] src/visualize.py (optional): pygame renderer and loop

Maps
- [ ] Add 1-2 more small maps to maps/ for testing

Tests
- [ ] tests/test_search.py: unit tests for BFS/DFS/UCS/A*
- [ ] tests/test_fog.py: unit tests for visible() and an integration test for OnlineAgent

Docs
- [ ] docs/assignment_summary.md: Fill in project summary
- [ ] docs/whatsapp_digest.md: Summarize decisions and roles from chat
- [ ] docs/decisions.md: Record design choices as they solidify

Tooling
- [ ] requirements.txt: add pytest; add pygame if/when GUI is used
- [ ] .vscode/settings.json: enable pytest discovery (optional)

Nice-to-have
- [ ] scripts/bench.py: benchmark harness once core modules exist
