"""Benchmark runner for Fog Maze.

Runs multiple algorithms on generated mazes across sizes, in fog and no-fog
modes, using the with-stats search wrappers to collect nodes expanded and
runtime. Outputs a CSV with one row per (size, algo, mode, seed) trial.

Usage (from repo root):

  # Quick sweep on 51..151 with step 50, 3 seeds, braid 0.10
  python scripts/bench.py --min 51 --max 151 --step 50 --seeds 3 --braid 0.10 --out reports/bench.csv

  # Restrict to a subset of algorithms and only no-fog mode
  python scripts/bench.py --algos bfs astar greedy --modes no-fog --min 51 --max 151 --step 50 --seeds 2 -o reports/bench_subset.csv

Notes
- Width==Height for simplicity. Sizes will be coerced to odd.
- "Fog" mode uses partial observability (agent discovers as it moves).
- "No-fog" mode gives the agent the full map (baseline performance).
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Iterable

from src.grid import Grid
from src.agent import OnlineAgent
from src.search import (
	ALGORITHMS_NEIGHBORS_WITH_STATS as SEARCH_WITH_STATS,
)
from scripts.maze_gen import generate_maze, write_csv as write_csv_map


def _odd(n: int) -> int:
	return n if n % 2 == 1 else n + 1


def _sizes(min_n: int, max_n: int, step: int) -> Iterable[int]:
	cur = min_n
	while cur <= max_n:
		yield _odd(cur)
		cur += max(1, step)


def _ensure_parent(path: Path) -> None:
	path.parent.mkdir(parents=True, exist_ok=True)


def run_trial(width: int, height: int, algo: str, mode: str, seed: int, braid: float) -> dict:
	"""Generate one maze and run a single (algo, mode) trial, returning a result dict."""
	# Generate and write a temporary map under maps/bench_tmp
	grid_2d = generate_maze(width, height, seed=seed, braid=braid)
	tmp_dir = Path("maps") / "bench_tmp"
	_ensure_parent(tmp_dir)
	tmp_path = tmp_dir / f"maze_{height}x{width}_b{int(braid*100)}_s{seed}.csv"
	write_csv_map(grid_2d, tmp_path)

	# Load grid and construct agent
	g = Grid.from_csv(tmp_path)
	full_map = (mode == "no-fog")
	search_fn = SEARCH_WITH_STATS[algo]
	agent = OnlineAgent(g, full_map=full_map, search_algo=search_fn)

	# Max steps: generous cap to avoid infinite runs; mazes are guaranteed solvable
	max_steps = width * height * 4
	m = agent.run(max_steps=max_steps)

	return {
		"width": width,
		"height": height,
		"algo": algo,
		"mode": mode,
		"seed": seed,
		"braid": braid,
		"reached": bool(m.reached_goal),
		"steps": int(m.steps),
		"cost": int(m.cost),
		"replans": int(m.replans),
		"nodes": int(getattr(m, "nodes_expanded", 0)),
		"runtime_sec": float(getattr(m, "runtime", 0.0)),
	}


def main(argv: list[str] | None = None) -> int:
	p = argparse.ArgumentParser(description="Benchmark Fog Maze algorithms over generated mazes.")
	p.add_argument("--min", dest="min_size", type=int, default=51, help="Minimum size (odd recommended)")
	p.add_argument("--max", dest="max_size", type=int, default=151, help="Maximum size (inclusive)")
	p.add_argument("--step", type=int, default=50, help="Size increment")
	p.add_argument("--seeds", type=int, default=3, help="Number of RNG seeds per size")
	p.add_argument("--braid", type=float, default=0.10, help="Dead-end braiding fraction [0..1]")
	p.add_argument("--algos", nargs="*", default=["bfs", "ucs", "astar", "greedy"], help="Algorithms to benchmark")
	p.add_argument(
		"--modes",
		nargs="*",
		default=["no-fog", "fog"],
		choices=["no-fog", "fog"],
		help="Agent modes to run",
	)
	p.add_argument("-o", "--out", type=str, default="reports/bench.csv", help="Output CSV path")
	args = p.parse_args(argv)

	out_path = Path(args.out)
	_ensure_parent(out_path)

	fieldnames = [
		"width",
		"height",
		"algo",
		"mode",
		"seed",
		"braid",
		"reached",
		"steps",
		"cost",
		"replans",
		"nodes",
		"runtime_sec",
	]

	with out_path.open("w", newline="", encoding="utf-8") as f:
		writer = csv.DictWriter(f, fieldnames=fieldnames)
		writer.writeheader()

		for n in _sizes(args.min_size, args.max_size, args.step):
			width = height = n
			for seed in range(args.seeds):
				for mode in args.modes:
					for algo in args.algos:
							try:
								row = run_trial(width, height, algo, mode, seed, braid=max(0.0, min(1.0, args.braid)))
							except Exception as e:
								# Print the exception to stderr to help diagnose failures while still
								# recording a placeholder row in the CSV. This keeps batch runs going.
								import traceback, sys
								print(f"[bench] Trial failed for n={n} seed={seed} mode={mode} algo={algo}: {e}", file=sys.stderr)
								traceback.print_exc()
								row = {
									"width": width,
									"height": height,
									"algo": algo,
									"mode": mode,
									"seed": seed,
									"braid": args.braid,
									"reached": False,
									"steps": -1,
									"cost": -1,
									"replans": -1,
									"nodes": -1,
									"runtime_sec": -1.0,
								}
							writer.writerow(row)

	print(f"Wrote benchmark CSV to {out_path}")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
