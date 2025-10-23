"""
Quickstart: minimal example showing how to call production code from experiments/ safely.

Why this exists
- Give teammates a tiny, copyable starter to run the core code from inside experiments/.
- Keep experiments isolated: do NOT import anything from experiments/ in src/ or tests/.

What it does
- Adds the project ROOT to sys.path so we can `import src.*` without packaging experiments.
- Runs a basic BFS on the sample map at maps/demo.csv and prints the path length.

How to run (PowerShell)
1) From repo root:
   python -m pip install -r requirements.txt  # optional now (no runtime deps yet)
2) Run this script:
   python experiments/_template/quickstart.py

If you copy this file into your own folder, adjust the relative path if needed.
"""
from __future__ import annotations

from pathlib import Path
import sys

# 1) Compute project ROOT by walking two levels up from this file:
# experiments/_template/quickstart.py -> experiments/ -> project ROOT
ROOT = Path(__file__).resolve().parents[2]

# 2) Put ROOT at the front of sys.path so `import src.*` works from experiments/
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Now we can import production modules from src/
try:
    from src.grid import Grid  # type: ignore
    from src.search import astar_neighbors  # type: ignore
except Exception as e:
    raise SystemExit(
        "Failed to import production modules from src/.\n"
        "Make sure you're running this from the project root and src/ exists.\n"
        f"Original error: {e}"
    )


def main() -> None:
    # Use the demo map shipped with the repo
    demo_map = ROOT / "maps" / "demo.csv"
    if not demo_map.exists():
        raise SystemExit(f"Demo map not found at {demo_map}")

    # Construct grid and run a simple A* (neighbors-based) from start to goal
    # Note: functions are placeholders in scaffold.
    g = Grid.from_csv(demo_map)
    g.reveal_from(g.start)

    def visible_neighbors(rc):
        return g.get_visible_neighbors(rc)

    start, goal = g.start, g.goal
    path = astar_neighbors(start, goal, visible_neighbors)

    # Summarize result without depending on visualization
    length = len(path) if path else None
    print("Quickstart result:")
    print(f"- Start: {start}")
    print(f"- Goal:  {goal}")
    print(f"- Path length: {length if length is not None else 'no path found'}")


if __name__ == "__main__":
    main()
