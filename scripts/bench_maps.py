"""
Benchmark existing map CSVs in a folder.

Loads all CSV maps under a directory and runs selected algorithms in fog and/or
no-fog modes using the stats-enabled search wrappers. Outputs a CSV summary.

Usage:
  python -m scripts.bench_maps --maps-dir maps/sweep_b30 --modes no-fog fog \
    --algos bfs dfs ucs astar greedy -o reports/bench_from_maps_b30.csv

Notes:
- Attempts to parse seed and braid from filenames of the form ..._bXX_sYY.csv, but
  leaves them as -1 if not present.
- Max steps is set to width*height*4 as a guard.
"""
from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path
from typing import Iterable, List, Tuple
from concurrent.futures import ProcessPoolExecutor, as_completed
import os

from src.grid import Grid
from src.agent import OnlineAgent
from src.search import ALGORITHMS_NEIGHBORS_WITH_STATS as SEARCH_WITH_STATS


def _iter_csvs(root: Path) -> Iterable[Path]:
    for p in sorted(root.glob("**/*.csv")):
        yield p


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _parse_braid_seed(name: str) -> tuple[int, int]:
    """Return (braid_percent, seed) if encoded in filename; else (-1, -1)."""
    # Expect patterns like ..._b30_s2.csv
    m_b = re.search(r"_b(\d+)", name)
    m_s = re.search(r"_s(\d+)", name)
    braid = int(m_b.group(1)) if m_b else -1
    seed = int(m_s.group(1)) if m_s else -1
    return braid, seed


def run_trial(map_path: Path, algo: str, mode: str, max_steps_factor: float) -> dict:
    g = Grid.from_csv(map_path)
    full_map = (mode == "no-fog")
    search_fn = SEARCH_WITH_STATS[algo]
    agent = OnlineAgent(g, full_map=full_map, search_algo=search_fn)
    # Guard steps to avoid very long trials; factor is configurable
    max_steps = int(g.width * g.height * max(1.0, float(max_steps_factor)))
    m = agent.run(max_steps=max_steps)

    braid_p, seed_num = _parse_braid_seed(map_path.name)

    return {
        "width": int(g.width),
        "height": int(g.height),
        "algo": algo,
        "mode": mode,
        "seed": int(seed_num),
        "braid": float(braid_p/100.0 if braid_p >= 0 else -1.0),
        "reached": bool(m.reached_goal),
        "steps": int(m.steps),
        "cost": int(m.cost),
        "replans": int(m.replans),
        "nodes": int(getattr(m, "nodes_expanded", 0)),
        "runtime_sec": float(getattr(m, "runtime", 0.0)),
        "map": map_path.name,
    }


def _build_jobs(maps_root: Path, modes: List[str], algos: List[str]) -> List[Tuple[Path, str, str]]:
    jobs: List[Tuple[Path, str, str]] = []
    for map_csv in _iter_csvs(maps_root):
        for mode in modes:
            for algo in algos:
                jobs.append((map_csv, mode, algo))
    return jobs


def main(argv: List[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Benchmark all CSV maps in a folder")
    p.add_argument("--maps-dir", required=True, help="Directory containing CSV maps")
    p.add_argument("--algos", nargs="*", default=["bfs", "ucs", "astar", "greedy"], help="Algorithms to run")
    p.add_argument(
        "--modes",
        nargs="*",
        default=["no-fog", "fog"],
        choices=["no-fog", "fog"],
        help="Agent modes to run",
    )
    p.add_argument("-o", "--out", dest="out_csv", default="reports/bench_from_maps.csv", help="Output CSV path")
    p.add_argument("--max-steps-factor", type=float, default=4.0, help="Max steps guard as width*height*factor (default 4.0)")
    p.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 2) - 1), help="Parallel workers (processes) for trials")
    args = p.parse_args(argv)

    maps_root = Path(args.maps_dir)
    out_path = Path(args.out_csv)
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
        "map",
    ]

    jobs = _build_jobs(maps_root, list(args.modes), list(args.algos))
    total = len(jobs)
    print(f"Discovered {total} trials under {maps_root} across modes/algorithms. Using {args.workers} workers.")

    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        # Run trials in parallel, but write results sequentially as they complete
        completed = 0
        with ProcessPoolExecutor(max_workers=int(args.workers)) as ex:
            futures = {ex.submit(run_trial, m, a, md, float(args.max_steps_factor)): (m, md, a) for (m, md, a) in jobs}
            for fut in as_completed(futures):
                map_csv, mode, algo = futures[fut]
                try:
                    row = fut.result()
                except Exception as e:
                    import traceback, sys
                    print(f"[bench_maps] Trial failed for {map_csv} mode={mode} algo={algo}: {e}", file=sys.stderr)
                    traceback.print_exc()
                    braid_p, seed_num = _parse_braid_seed(map_csv.name)
                    row = {
                        "width": -1,
                        "height": -1,
                        "algo": algo,
                        "mode": mode,
                        "seed": int(seed_num),
                        "braid": float(braid_p/100.0 if braid_p >= 0 else -1.0),
                        "reached": False,
                        "steps": -1,
                        "cost": -1,
                        "replans": -1,
                        "nodes": -1,
                        "runtime_sec": -1.0,
                        "map": map_csv.name,
                    }
                writer.writerow(row)
                completed += 1
                if completed % 20 == 0 or completed == total:
                    print(f"Progress: {completed}/{total} trials written ({completed/total:.0%})")

    print(f"Wrote benchmark CSV to {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
