TL;DR: CSV grid with comma-separated tokens: S (start), G (goal), 0 (free), 1 (wall). Rows must be same length.

Map format (CSV):
- Use unquoted tokens: 0 = free, 1 = wall, S = start, G = goal
- Comma-separated rows, consistent row length required
- Example (first two rows of a map):

```
S,0,0,1
0,1,0,0
```

- See `demo.csv` and `demo2.csv` for full examples.

Edge-case maps (for tests and demos)
- boxed_start.csv — Start is surrounded by walls on most sides; tests visibility of walls and no-move behavior under fog.
- corridor_straight.csv — Straight corridor from S to G; good for A* and visibility growth sanity.
- corridor_turn.csv — Corridors with a 90° turn; ensures re-planning behaves under fog when the corner is revealed.
- dead_end_maze.csv — Multiple dead-ends requiring backtracking.
- open_room.csv — Small room with open area; good for overlay/visual tests.
