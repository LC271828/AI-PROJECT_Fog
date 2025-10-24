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

# Compute project ROOT by walking two levels up from this file:
# experiments/asthar/grid.py -> experiments/ -> project ROOT
ROOT = Path(__file__).resolve().parents[2]
from dataclasses import dataclass, field
from typing import List, Tuple

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

    # === Stage 2 — Map loading (CSV) ===
    # [ ] Implement from_csv(path: PathLike) -> Grid
    #       - Read CSV strictly (comma-separated), validate rectangular shape
    #       - Validate allowed symbols only: {"0","1","S","G"}
    #       - Locate exactly one S and one G; raise if missing/duplicates
    #       - Build grid (2D list[str]) and visible mask (all False)
    #       - Set width/height and default fog_radius
    def from_csv(self, map: Path):

        # Open .csv file
        # [ ] Implement from_csv(path: PathLike) -> Grid
        # - Read CSV strictly (comma-separated)
        with open(map, newline='') as csvfile:

            # Local Variables:
            S_count = 0
            G_count = 0

            # Open reader object
            mapreader = csv.reader(csvfile)

            # FOR loop to go through every row in .csv file
            # and input into "grid" array
            # - Set width/height and default fog_radius
            for row in mapreader:
                self.grid.append(row)

                self.width = 0

                # IF statement logic error
                # - Validate rectangular shape
                if len(self.grid[self.height]) != len(self.grid[self.height]):
                    print("Maze does not have a rectangular shape")
                    #sys.exit(1)

                else:
                    # - Validate allowed symbols only: {"0","1","S","G"}
                    for element in self.grid[self.height]:
                        if element != "1" and element != "0" and element != "S" and element != "G":
                            print(f"Invalid Element: {element}")
                            #sys.exit(1)

                        # - Locate exactly one S and one G; raise if missing/duplicates
                        # Count number of starting/goal positions and check if multiple
                        # starting/goal positions are present
                        elif element == "S":
                            S_count += 1

                            if S_count > 1:
                                print("Multiple starting positions found")
                                #sys.exit(1)
                            else:
                                self.start = (self.height, self.width)

                        elif element == "G":
                            G_count += 1

                            if G_count > 1:
                                print("Multiple goal positions found")
                                #sys.exit(1)
                            else:
                                self.goal = (self.height, self.width)
                    
                        self.width += 1

                self.height += 1
            
            # Check for existence of starting/goal positions
            if S_count == 0:
                print("No starting positions found")
            elif G_count == 0:
                print("No goal positions found")

            # Fill the "visible" grid with False and adjust it to be the
            # same size as the "grid"
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

        if (self.in_bounds(r, c) == True):

            # Variables and arrays
            neighbors: list[tuple[int, int]] = []

            # Find neighboring tiles using current position.
            # Appends north, east, south and west only.
            for y in range(r-1, r+2):

                if (y == r):
                    neighbors.append((y, c-1))
                    neighbors.append((y, c+1))
                else:
                    neighbors.append((y, c))
        
            return neighbors
    
        else:
            return []
    
    # [ ] tile_at(r: int, c: int) -> str       # returns map symbol
    def tile_at(self, r, c):
        if (self.in_bounds(r, c) == True):
            return self.grid[r][c]
        #else:
            #return "Given tile is out of bounds"

    # [ ] is_visible(r: int, c: int) -> bool   # visible[r][c]
    def is_visible(self, r, c):
        if (self.in_bounds(r, c) == True):
            if (self.visible[r][c] != False):
                return True
            else:
                return False
        #else:
            #return "Given tile is out of bounds"
        
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

def main():

    neighbors: list[tuple[int, int]] = []
    revealed: list[tuple[int, int]] = []
    visible_neighbors: list[tuple[int, int]] = []
    visible_tiles: list[tuple[int, int]] = []

    # Use the demo map shipped with the repo
    demo_map = ROOT / "maps" / "demo.csv"
    if not demo_map.exists():
        raise SystemExit(f"Demo map not found at {demo_map}")

    # Make new object while passing the file path for the map
    g = Grid()
    g.from_csv(map=demo_map)

    print("Height:", g.height)
    print("Width:", g.width)

    # FOR loop to output grid or visible
    for row in g.grid:
        print(row)

    print("\n")

    for row in g.visible:
        print(row)

    print("\n(8,7) is within bounds:", g.in_bounds(8,7))
    print("(4,3) is a wall:", g.is_wall(4,3))
    print("(1,2) is passable:", g.passable(1,2))

    print("\nList of neighbors of (2,3)")
    neighbors = g.neighbors4(2,3)
    print(neighbors)

    print("\nAgent moves to (1,0)")
    revealed = g.reveal_from((1,0))
    print(revealed)

    for row in g.visible:
        print(row)
    
    print("\nCheck visible neighbors of (2,0)")
    visible_neighbors = g.get_visible_neighbors((2,0))
    print(visible_neighbors)

    print("\nAgent moves to (2,0)")
    revealed = g.reveal_from((2,0))
    print(revealed)

    for row in g.visible:
        print(row)
    
    print("\nCheck visible neighbors of (2,0) again")
    visible_neighbors = g.get_visible_neighbors((2,0))
    print(visible_neighbors)

    print("\nEvery visible tile coords")
    visible_tiles = g.visible_tiles()
    print(visible_tiles)
    
# Ensure main() is executed first (probably not needed here tho)
if __name__ == "__main__":
    main()