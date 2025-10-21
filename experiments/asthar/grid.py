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
    map: Path      # Store .csv file path
    grid: list[list[str]] = field(default_factory=list)     # 2D array initialized with empty list
    start: tuple[int, int] = (0, 0)
    goal:  tuple[int, int] = (0, 0)
    #visible: list[list[bool]] # same shape as grid, all False initially
    height: int = 1
    width: int = 1
    #fog_radius: int           # fixed at 1 for this project (visibility one step)

    # Constructor for reading .csv file
    # === Stage 2 — Map loading (CSV) ===
    #       - Build grid (2D list[str]) and visible mask (all False)
    #       - Set width/height and default fog_radius

    def __post_init__(self):

        # Open .csv file
        # [ ] Implement from_csv(path: PathLike) -> Grid
        # - Read CSV strictly (comma-separated)
        with open(self.map, newline='') as csvfile:

            # Local Variables:
            S_count = 0
            G_count = 0

            self.grid = [['1']]

            # Open reader object
            mapreader = csv.reader(csvfile)

            # FOR loop to go through every row in .csv file
            # and input into "grid" array
            for row in mapreader:
                self.grid.append(row)
                self.grid[self.height].append('1')
                self.grid[self.height].insert(0, '1')

                self.width = 0
            
                # Note: Last row of walls has not been added yet so dw about
                # IF statement logic error
                # - Validate rectangular shape
                if len(self.grid[self.height]) != len(self.grid[self.height - 1]) and self.height > 1:
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

            # Fullfill first row of walls
            for element in range(len(self.grid[1]) - 1):
                self.grid[0].append('1')

            # Add last row of walls
            end_row = ['1'] * len(self.grid[1])
            self.grid.append(end_row)

            # - Set width/height and default fog_radius
            # Increment to find true height of maze
            self.height += 1

            # Width = len(self.grid[1])
            self.width = len(self.grid[1])

            print(self.height)
            print(self.width)
            print(self.start)
            print(self.goal)

def main():

    # Use the demo map shipped with the repo
    demo_map = ROOT / "maps" / "demo.csv"
    if not demo_map.exists():
        raise SystemExit(f"Demo map not found at {demo_map}")

    # Make new object while passing the file path for the map
    g = Grid(map=demo_map)

    # FOR loop to output each row of the "grid" array in "g" object
    for row in g.grid:
        print(row)
        #print(len(row))

# Ensure main() is executed first (probably not needed here tho)
if __name__ == "__main__":
    main()