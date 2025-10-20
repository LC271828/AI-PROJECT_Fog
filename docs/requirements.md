Functional requirements:
- Load grid map from CSV with 0/1/S/G
- Implement DFS/BFS/UCS/A* search (A* uses Manhattan heuristic)
- Fog-of-war with visibility radius 1 (U/D/L/R only); walls revealed and block reveal beyond; no re-fogging
- Online agent that re-plans as new cells are revealed; reaches goal on demo map
- Optional Pygame visualisation (fog mask, visible walls, path)

Non-functional:
- Simple CLI
- Unit tests for algorithms and fog/agent
- Branch workflow: main → dev → feat/...
