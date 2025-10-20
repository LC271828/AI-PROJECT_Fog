Architectural decisions:
- Separation of concerns: grid/search/agent/visualize
- Headless-first design; GUI optional
- CSV maps for version control
- Online agent with frontier exploration when goal is unknown/unreachable on known map

Project-wide conventions:
- Movement: up/down/left/right only (no diagonals)
- Fog: radius 1; walls visible when adjacent and block reveal beyond; no re-fogging
- Heuristic: Manhattan for A*
- Re-planning: Agent re-runs search as visibility expands
- Branch workflow: main (final) and dev (integration)
