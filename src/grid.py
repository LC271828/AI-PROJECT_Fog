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



# ===== Begin copied implementation from experiments/asthar/grid.py (verbatim) =====
# Context
# - Map format: CSV (see maps/README.md) with symbols: 0=free, 1=wall, S=start, G=goal.
# - Moves: 4-connected (up/down/left/right) only; no diagonal movement.
# - Fog: fixed radius of 1 (up/down/left/right only). Walls become visible when in range and block any further reveal beyond them. No re-fogging: once visible, a cell stays visible.

# Goal
# Provide a clean interface so the Agent can ask “what can I see?” and “where can I move?”
# without knowing the map internals.
# """

# For reading demo.py from "maps" folder
from __future__ import annotations

from pathlib import Path
import sys

# For reading CSV files
import csv

from dataclasses import dataclass, field
from typing import List, Tuple

# CLEANUP: Removed unused ROOT variable from earlier experimental import context.

# Grid class
# === Stage 1 — Basic data structure ===
@dataclass
class Grid:
	grid: list[list[str]] = field(default_factory=list)     # 2D array initialized with empty list
	start: tuple[int, int] = (0, 0)     # Start tuple intialized
	goal:  tuple[int, int] = (0, 0)     # Goal tuple initialized
	visible: list[list[bool]] = field(default_factory=list)         # same shape as grid, all False initially
	height: int = 0
	width: int = 0
	#fog_radius: int           # fixed at 1 for this project (visibility one step)

	# TEAM_API: Provide a factory classmethod that loads from CSV and returns a Grid
	# This keeps the stricter validation centralized in the existing _from_csv loader.
	@classmethod
	def from_csv(cls, path: Path) -> "Grid":
		"""Load a Grid from a CSV file path and return a new instance.

		TEAM_API-compliant constructor. Uses the instance loader under the hood
		to preserve validation and initialization in one place.
		"""
		g = cls()
		g._from_csv(path)
		return g

	# === Stage 2 — Map loading (CSV) ===
	# [ ] Implement from_csv(path: PathLike) -> Grid
	#       - Read CSV strictly (comma-separated), validate rectangular shape
	#       - Validate allowed symbols only: {"0","1","S","G"}
	#       - Locate exactly one S and one G; raise if missing/duplicates
	#       - Build grid (2D list[str]) and visible mask (all False)
	#       - Set width/height and default fog_radius
	def _from_csv(self, map: Path):
		# CHANGE: reworked CSV load to enforce rectangular shape and strict validation.
		# - Track expected_width from the first row; ensure all rows match.
		# - Validate symbols; count exactly one S and one G.
		# - Raise ValueError for any violations (do not print/exit).
		rows: list[list[str]] = []
		with open(map, newline='') as csvfile:
			reader = csv.reader(csvfile)
			for row in reader:
				rows.append(row)

		if not rows:
			raise ValueError("Map CSV is empty")  # CHANGE: strict error

		expected_width = len(rows[0])  # CHANGE: rectangular shape tracking
		s_count = 0
		g_count = 0
		s_pos = (0, 0)
		g_pos = (0, 0)

		for r, row in enumerate(rows):
			if len(row) != expected_width:
				# CHANGE: raise on non-rectangular shape
				raise ValueError(f"Non-rectangular map at row {r}: expected {expected_width}, got {len(row)}")
			for c, element in enumerate(row):
				if element not in {"0", "1", "S", "G"}:
					# CHANGE: raise on illegal symbol
					raise ValueError(f"Invalid element '{element}' at ({r},{c})")
				if element == "S":
					s_count += 1
					s_pos = (r, c)
				elif element == "G":
					g_count += 1
					g_pos = (r, c)

		if s_count != 1:
			# CHANGE: enforce exactly one S
			raise ValueError(f"Expected exactly one 'S', found {s_count}")
		if g_count != 1:
			# CHANGE: enforce exactly one G
			raise ValueError(f"Expected exactly one 'G', found {g_count}")

		# CHANGE: compute width/height once from validated rows
		self.grid = rows
		self.height = len(rows)
		self.width = expected_width
		self.start = s_pos
		self.goal = g_pos

		# Initialize visibility mask (all hidden)
		self.visible = [[False for _ in range(self.width)] for _ in range(self.height)]

	# === Stage 3 — Core helpers (public API) ===
	# [ ] in_bounds(r: int, c: int) -> bool
	# [ ] is_wall(r: int, c: int) -> bool
	# [ ] passable(r: int, c: int) -> bool     # not a wall
	# [ ] neighbors4(r: int, c: int) -> list[tuple[int,int]]  # 4-connected only
	# [ ] tile_at(r: int, c: int) -> str       # returns map symbol
	# [ ] is_visible(r: int, c: int) -> bool   # visible[r][c]

	# [ ] in_bounds(r: int, c: int) -> bool
	def in_bounds(self, r, c):
		if (r >= 0 and r < self.height and c >= 0 and c < self.width):
			return True
		else:
			return False
        
	# [ ] is_wall(r: int, c: int) -> bool
	def is_wall(self, r, c):
		if (self.in_bounds(r,c) == True):
			if (self.grid[r][c] == "1"):
				return True
			else:
				return False
		#else:
			#return "Given tile is out of bounds"
        
	# [ ] passable(r: int, c: int) -> bool     # not a wall
	def passable(self, r, c):
		if (self.in_bounds(r,c) == True):
			if (self.grid[r][c] == "0" or self.grid[r][c] == "S" or self.grid[r][c] == "G"):
				return True
			else:
				return False
		#else:
			#return
        
	# [ ] neighbors4(r: int, c: int) -> list[tuple[int,int]]  # 4-connected only
	def neighbors4(self, r, c):
		# CHANGE: return only in-bounds 4-connected neighbors (U/R/D/L)
		if not self.in_bounds(r, c):
			return []
		cand = [(r-1, c), (r, c+1), (r+1, c), (r, c-1)]
		return [(rr, cc) for (rr, cc) in cand if self.in_bounds(rr, cc)]
    
	# [ ] tile_at(r: int, c: int) -> str       # returns map symbol
	def tile_at(self, r, c):
		if (self.in_bounds(r, c) == True):
			return self.grid[r][c]
		#else:
			#return "Given tile is out of bounds"

	# [ ] is_visible(r: int, c: int) -> bool   # visible[r][c]
	def is_visible(self, r, c):
		# CHANGE: out-of-bounds is not visible (return False explicitly)
		if not self.in_bounds(r, c):
			return False
		return bool(self.visible[r][c])
        
	# === Stage 4 — Fog logic (radius = 1) ===
	# Note: Visibility is one step in 4 directions. Walls are revealed but block any reveal past them. No re-fogging.
	# [ ] reveal_from(pos: Coord) -> list[Coord]
	#       - Mark current cell visible
	#       - For each of the four directions (U/D/L/R):
	#           - Reveal the adjacent cell if in_bounds
	#           - If that adjacent cell is a wall, do not reveal anything beyond it
	# [ ] get_visible_neighbors(pos: Coord) -> list[Coord]
	#       - Only neighbors that are in bounds, visible, and passable
	# [ ] visible_tiles() -> list[tuple[int,int]]
	#       - Return all coordinates where visible is True
	#       - Once visible[r][c] is True, it must remain True (no re-fogging)

	# [ ] reveal_from(pos: Coord) -> list[Coord]
	def reveal_from(self, pos: tuple[int,int]):
            
		# Local Variables
		neighbors: list[tuple[int, int]] = []
		revealed: list[tuple[int, int]] = []

		# Call "neighbors4" class method and fill "neighbors" list
		neighbors = self.neighbors4(pos[0], pos[1])

		if (self.visible[pos[0]][pos[1]] == False):
			self.visible[pos[0]][pos[1]] = True
			revealed.append((pos[0], pos[1]))

		# Check if each coords in "neighbors" corresponds to a hidden (False) tile in "visible".
		# If yes then set hidden tile into true in "visible" and add coords to "revealed".
		for tuple_index in range(len(neighbors)):
			if (self.is_visible(neighbors[tuple_index][0], neighbors[tuple_index][1]) == False):
				self.visible[neighbors[tuple_index][0]][neighbors[tuple_index][1]] = True
				revealed.append(neighbors[tuple_index])

		return revealed
        
	# [ ] get_visible_neighbors(pos: Coord) -> list[Coord]
	def get_visible_neighbors(self, pos: tuple[int,int]):
            
		# Local Variables
		neighbors: list[tuple[int, int]] = []
		visible_neighbors: list[tuple[int, int]] = []

		# Call "neighbors4" class method and fill "neighbors list"
		neighbors = self.neighbors4(pos[0], pos[1])

		# Checks through "neighbors" list
		# If an element is in bounds, visible and passable then it gets added to the "visible_neighbors" list
		for tuple_index in range(len(neighbors)):
			if (self.in_bounds(neighbors[tuple_index][0], neighbors[tuple_index][1]) == True and
				self.is_visible(neighbors[tuple_index][0], neighbors[tuple_index][1]) == True and
				self.passable(neighbors[tuple_index][0], neighbors[tuple_index][1]) == True):
				visible_neighbors.append(neighbors[tuple_index])

		return visible_neighbors
    
	# [ ] visible_tiles() -> list[tuple[int,int]]
	def visible_tiles(self):

		# Local Variables
		visible_tiles: list[tuple[int, int]] = []

		# Check every element in "visible" mask and
		# append it into "visible_tiles" list if it is revealed
		for r in range(0, self.height):
			for c in range(0, self.width):

				if (self.is_visible(r, c) == True):
					visible_tiles.append((r, c))

		return visible_tiles

# (Demo code removed from src; see scripts/demo_grid.py for a runnable demo.)
# ===== End copied implementation from experiments/asthar/grid.py =====

