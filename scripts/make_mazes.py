"""
Batch maze generator.

Creates a set of maze CSVs under an output directory, sweeping sizes using a
multiplicative schedule (e.g., 5, 10, 20, 40, ...) until a maximum. Each size
is coerced to odd (generator requirement). Multiple seeds per size supported.

Usage examples:
  # Geometric sizes starting at 5, doubling until <= 320, 5 seeds, high braid
  python -m scripts.make_mazes --out maps/sweep_b30 --start 5 --factor 2 --max 320 --seeds 5 --braid 0.30

Notes
- The generator ensures odd dimensions; filenames reflect the actual grid size.
- "braid" is the fraction of dead-ends converted into loops (0=no loops, 0.3=some).
"""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import List

from scripts.maze_gen import generate_maze, write_csv


def _parse_args(argv: List[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Batch-generate maze CSVs")
    p.add_argument("--out", dest="out_dir", required=True, help="Output directory for generated CSV maps")
    p.add_argument("--start", type=int, default=5, help="Starting size (width=height)")
    p.add_argument("--factor", type=float, default=2.0, help="Multiplicative growth factor for sizes")
    p.add_argument("--max", dest="max_size", type=int, default=320, help="Maximum size (inclusive, before odd coercion)")
    p.add_argument("--seeds", type=int, default=5, help="Number of RNG seeds per size")
    p.add_argument("--braid", type=float, default=0.30, help="Dead-end braiding fraction [0..1]")
    return p.parse_args(argv)


def _ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def main(argv: List[str] | None = None) -> int:
    args = _parse_args(argv)
    out_dir = Path(args.out_dir)
    _ensure_dir(out_dir)

    # Generate sizes on a geometric progression
    sizes: List[int] = []
    n = max(1, int(args.start))
    factor = max(1.01, float(args.factor))  # avoid infinite loops if factor <= 1
    while n <= int(args.max_size):
        sizes.append(n)
        n = int(n * factor)
        if n == sizes[-1]:  # ensure progress
            n += 1

    # For each size and seed, generate and write a CSV
    for sz in sizes:
        for seed in range(args.seeds):
            grid = generate_maze(sz, sz, seed=seed, braid=max(0.0, min(1.0, args.braid)))
            H = len(grid)
            W = len(grid[0]) if H else 0
            fname = f"maze_{W}x{H}_b{int(args.braid*100)}_s{seed}.csv"
            out_path = out_dir / fname
            write_csv(grid, out_path)
            print(f"Wrote {out_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
