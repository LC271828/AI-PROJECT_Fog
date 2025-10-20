"""Grid module (TODO).

Context
- Map format: CSV (see maps/README.md) with symbols: 0=free, 1=wall, S=start, G=goal.
- Moves: 4-connected (up/down/left/right) only; no diagonal movement.
- Fog: fixed radius of 1 (up/down/left/right only). Walls become visible when in range and block any further reveal beyond them. No re-fogging: once visible, a cell stays visible.

Goal
Provide a clean interface so the Agent can ask “what can I see?” and “where can I move?”
without knowing the map internals.
"""

# === Stage 1 — Basic data structure ===
# [ ] Define a Grid class (prefer @dataclass).
#     Fields:
#       - grid: list[list[str]]     # '0' free, '1' wall, 'S' start, 'G' goal (kept as read)
#       - start: tuple[int, int]
#       - goal:  tuple[int, int]
#       - visible: list[list[bool]] # same shape as grid, all False initially
#       - height: int
#       - width: int
#       - fog_radius: int           # fixed at 1 for this project (visibility one step)

# === Stage 2 — Map loading (CSV) ===
# [ ] Implement from_csv(path: PathLike) -> Grid
#       - Read CSV strictly (comma-separated), validate rectangular shape
#       - Validate allowed symbols only: {"0","1","S","G"}
#       - Locate exactly one S and one G; raise if missing/duplicates
#       - Build grid (2D list[str]) and visible mask (all False)
#       - Set width/height and default fog_radius

# === Stage 3 — Core helpers (public API) ===
# [ ] in_bounds(r: int, c: int) -> bool
# [ ] is_wall(r: int, c: int) -> bool
# [ ] passable(r: int, c: int) -> bool     # not a wall
# [ ] neighbors4(r: int, c: int) -> list[tuple[int,int]]  # 4-connected only
# [ ] tile_at(r: int, c: int) -> str       # returns map symbol
# [ ] is_visible(r: int, c: int) -> bool   # visible[r][c]

# === Stage 4 — Fog logic (radius = 1) ===
# NOTE: Visibility is one step in 4 directions. Walls are revealed but block any reveal past them. No re-fogging.
# [ ] reveal_from(pos: tuple[int,int]) -> None
#       - Mark current cell visible
#       - For each of the four directions (U/D/L/R):
#           - Reveal the adjacent cell if in_bounds
#           - If that adjacent cell is a wall, do not reveal anything beyond it
# [ ] get_visible_neighbors(pos: tuple[int,int]) -> list[tuple[int,int]]
# [ ] get_visible_neighbors(pos: tuple[int,int]) -> list[tuple[int,int]]
#       - Return neighbors4(pos) filtered by in_bounds AND is_visible AND passable
# [ ] visible_tiles() -> list[tuple[int,int]]
#       - Return all coordinates where visible is True
#       - Once visible[r][c] is True, it must remain True (no re-fogging)

# === Stage 5 — Debug / Testing aids ===
# [ ] __str__() or print_masked() -> str
#       - Render map where hidden cells are '?' and visible cells show their actual symbols
# [ ] Tiny driver (optional, for manual testing only — keep out of unit tests):
#       - load demo map, reveal_from(start), print masked, step once, reveal again, print

# === Stage 6 — Integration readiness ===
# Ensure the following minimal API exists for Agent and CLI wiring:
# [ ] grid.reveal_from(pos)
# [ ] grid.get_visible_neighbors(pos)
# [ ] grid.start, grid.goal
# [ ] Optional: to_dict() for metrics/logging snapshots (visible coverage, etc.)

# === Edge cases & validation ===
# [ ] Handle maps with inconsistent row lengths (raise ValueError)
# [ ] Handle illegal characters (raise ValueError with location)
# [ ] Enforce exactly one S and one G (raise ValueError otherwise)
# [ ] Bounds-safe helpers; never index grid without in_bounds check

# Implementation will be added after search/agent contracts are finalized.

