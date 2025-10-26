"""
Maze generator for Fog Maze project.

Generates rectangular CSV maps with symbols {0,1,S,G}:
- 1 = wall
- 0 = free
- S = start (default: top-left interior)
- G = goal  (default: bottom-right interior)

Algorithm
- Perfect maze via iterative DFS (recursive backtracker) over a grid of odd
  dimensions (cells at odd coordinates). Corridors are carved two steps at a time.
- Optional "braid" step removes a fraction of dead-end walls to add loops and
  increase branching, which helps show differences in search algorithms.

Usage (from repo root):
  python scripts/maze_gen.py --width 101 --height 101 --braid 0.10 --seed 42 --out maps/maze_101x101_braid10.csv

Notes
- Width/height should be odd numbers >= 5.
- The generator ensures at least one path between S and G in a perfect maze.
- With braiding (>0), the maze will contain loops; S-G connectivity remains.
"""
from __future__ import annotations

import argparse
import random
from pathlib import Path
from typing import List, Tuple


def _ensure_odd(n: int) -> int:
    """Return an odd integer by adding 1 if ``n`` is even."""
    if n % 2 == 1:
        return n
    else:
        return n + 1


def generate_maze(width: int, height: int, seed: int | None = None, braid: float = 0.0) -> List[List[str]]:
    """Generate a maze as a 2D list of map symbols ('0','1','S','G').

    Parameters
    - width, height: desired dimensions (odd recommended). Will be coerced to odd.
    - seed: RNG seed for reproducibility.
    - braid: fraction in [0,1] of dead-ends to "braid" (remove a wall to create a loop).

    Returns: 2D array of strings (CSV-ready) with rectangular shape.
    """
    rng = random.Random(seed)
    W = _ensure_odd(max(5, width))
    H = _ensure_odd(max(5, height))

    # Initialize all walls
    grid = [["1" for _ in range(W)] for _ in range(H)]

    # Carve with iterative DFS over cells at odd coordinates
    start = (1, 1)
    stack: List[Tuple[int, int]] = [start]
    grid[start[0]][start[1]] = "0"

    def neighbors2(r: int, c: int) -> List[Tuple[int, int, int, int]]:
        # Return list of (nr, nc, wr, wc) where (wr,wc) is wall between current and neighbor
        out: List[Tuple[int, int, int, int]] = []
        for dr, dc in [(-2, 0), (0, 2), (2, 0), (0, -2)]:
            nr, nc = r + dr, c + dc
            wr, wc = r + dr // 2, c + dc // 2
            if 1 <= nr < H - 1 and 1 <= nc < W - 1 and grid[nr][nc] == "1":
                out.append((nr, nc, wr, wc))
        rng.shuffle(out)
        return out

    while stack:
        r, c = stack[-1]
        nbrs = neighbors2(r, c)
        if not nbrs:
            stack.pop()
            continue
        nr, nc, wr, wc = nbrs.pop()
        # carve wall and neighbor cell
        grid[wr][wc] = "0"
        grid[nr][nc] = "0"
        stack.append((nr, nc))

    # Braid: remove walls next to dead ends to make loops
    if braid > 0.0:
        def is_dead_end(rr: int, cc: int) -> bool:
            if grid[rr][cc] != "0":
                return False
            cnt = 0
            for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
                r2, c2 = rr+dr, cc+dc
                if 0 <= r2 < H and 0 <= c2 < W and grid[r2][c2] == "0":
                    cnt += 1
            return cnt == 1
        dead_cells = [(r,c) for r in range(1,H-1) for c in range(1,W-1) if is_dead_end(r,c)]
        rng.shuffle(dead_cells)
        target = int(len(dead_cells) * braid)
        made = 0
        for r, c in dead_cells:
            if made >= target:
                break
            # Find a neighboring wall that separates this dead-end from another corridor and remove it
            candidates: List[Tuple[int,int]] = []
            for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
                wr, wc = r+dr, c+dc
                r2, c2 = r+2*dr, c+2*dc
                if 0 <= wr < H and 0 <= wc < W and 0 <= r2 < H and 0 <= c2 < W:
                    if grid[wr][wc] == "1" and grid[r2][c2] == "0":
                        candidates.append((wr, wc))
            if candidates:
                wr, wc = rng.choice(candidates)
                grid[wr][wc] = "0"
                made += 1

    # Place S and G at corners inside the boundary
    grid[1][1] = "S"
    grid[H-2][W-2] = "G"

    return grid


def write_csv(grid: List[List[str]], out_path: Path) -> None:
    lines = [",".join(row) for row in grid]
    out_path.write_text("\n".join(lines), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Generate a maze CSV (0/1/S/G)")
    p.add_argument("--width", type=int, default=101, help="Width (odd >=5)")
    p.add_argument("--height", type=int, default=101, help="Height (odd >=5)")
    p.add_argument("--seed", type=int, default=None, help="RNG seed")
    p.add_argument("--braid", type=float, default=0.0, help="Fraction of dead-ends to braid into loops [0..1]")
    p.add_argument("--out", type=str, default=None, help="Output CSV path (default: maps/maze_<WxH>_b<braid*100>.csv)")
    args = p.parse_args(argv)

    grid = generate_maze(args.width, args.height, seed=args.seed, braid=max(0.0, min(1.0, args.braid)))
    if args.out:
        out = Path(args.out)
    else:
        default_name = f"maze_{grid[0].__len__()}x{len(grid)}_b{int(args.braid*100)}.csv"
        out = Path("maps") / default_name
    out.parent.mkdir(parents=True, exist_ok=True)
    write_csv(grid, out)
    print(f"Wrote maze to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
