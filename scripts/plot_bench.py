"""
Plot benchmark CSV produced by scripts.bench.

Generates runtime-vs-size (and cost-vs-size) curves per algorithm with mean and
std-dev across seeds. Optionally filter by mode (fog/no-fog).

Usage examples:
  python -m scripts.plot_bench --in reports/bench.csv --metric runtime --mode no-fog
  python -m scripts.plot_bench --in reports/bench.csv --metric cost --mode fog
  python -m scripts.plot_bench --in reports/bench.csv --out reports/plots --metric runtime --mode no-fog

Notes
- Requires matplotlib. If not installed, prints a helpful message.
- Input CSV columns are those produced by scripts.bench.
"""
from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple


def _parse_args(argv: List[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Plot benchmark CSV from scripts.bench")
    p.add_argument("--in", dest="input_csv", required=True, help="Input CSV path from scripts.bench")
    p.add_argument("--out", dest="out_dir", default="reports/plots", help="Output directory for plots")
    p.add_argument("--metric", choices=["runtime", "cost"], default="runtime", help="Metric to plot: runtime or cost")
    p.add_argument("--mode", choices=["fog", "no-fog", "both"], default="no-fog", help="Filter mode to plot")
    p.add_argument("--title", default=None, help="Optional plot title")
    p.add_argument("--file-prefix", default=None, help="Optional prefix for output filenames")
    return p.parse_args(argv)


def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def load_data(input_csv: Path) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    with input_csv.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def aggregate(rows: List[Dict[str, str]], metric: str, mode_filter: str) -> Tuple[Dict[Tuple[str, int], float], Dict[Tuple[str, int], float], List[int], List[str]]:
    """Aggregate mean and std-dev by (algo, size).

    Returns (means, stds, sorted_sizes, algos)
    """
    # Filter by mode if requested
    if mode_filter != "both":
        rows = [r for r in rows if r.get("mode") == mode_filter]

    # Build buckets by (algo, size)
    values: Dict[Tuple[str, int], List[float]] = defaultdict(list)
    algos_set = set()
    sizes_set = set()
    for r in rows:
        try:
            algo = str(r["algo"])  # type: ignore
            size = int(r["width"])  # width == height in bench
            reached = str(r.get("reached", "True")).lower() == "true"
            if metric == "runtime":
                val = float(r.get("runtime_sec", 0.0))
            else:
                val = float(r.get("cost", 0.0))
        except Exception:
            continue
        # Optionally, keep only successful trials for cost
        if metric == "cost" and not reached:
            continue
        # Keep values
        values[(algo, size)].append(val)
        algos_set.add(algo)
        sizes_set.add(size)

    # Compute mean and std-dev per bucket
    means: Dict[Tuple[str, int], float] = {}
    stds: Dict[Tuple[str, int], float] = {}
    for key, vs in values.items():
        if not vs:
            continue
        n = float(len(vs))
        mean = sum(vs) / n
        # std-dev (population) to visualize variability; robust enough for our use
        var = sum((x - mean) ** 2 for x in vs) / n
        std = var ** 0.5
        means[key] = mean
        stds[key] = std

    sizes = sorted(sizes_set)
    algos = sorted(algos_set)
    return means, stds, sizes, algos


def plot_curves(means: Dict[Tuple[str, int], float], stds: Dict[Tuple[str, int], float], sizes: List[int], algos: List[str], metric: str, out_dir: Path, title: str | None = None, file_prefix: str | None = None, mode_label: str = "") -> Path | None:
    try:
        import matplotlib.pyplot as plt  # type: ignore
    except Exception:
        print("Matplotlib is required for plotting. Install with: python -m pip install matplotlib")
        return None

    metric_label = "Average Runtime (s)" if metric == "runtime" else "Average Cost (steps)"
    fig, ax = plt.subplots(figsize=(8, 5))

    for algo in algos:
        ys: List[float] = []
        es: List[float] = []
        for n in sizes:
            ys.append(means.get((algo, n), float("nan")))
            es.append(stds.get((algo, n), 0.0))
        ax.errorbar(sizes, ys, yerr=es, marker="o", capsize=3, label=algo)

    ax.set_xlabel("Maze size (width = height)")
    ax.set_ylabel(metric_label)
    if title:
        ax.set_title(title)
    elif mode_label:
        ax.set_title(f"{metric_label} vs Size ({mode_label})")
    else:
        ax.set_title(f"{metric_label} vs Size")
    ax.legend(title="Algorithm")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()

    _ensure_dir(out_dir)
    stem = file_prefix or f"plot_{metric}"
    if mode_label:
        stem += f"_{mode_label.replace('-', '')}"
    out_path = out_dir / f"{stem}.png"
    fig.savefig(str(out_path), dpi=144)
    print(f"Wrote plot to {out_path}")
    return out_path


def main(argv: List[str] | None = None) -> int:
    args = _parse_args(argv)
    in_csv = Path(args.input_csv)
    if not in_csv.exists():
        print(f"Input CSV not found: {in_csv}")
        return 2

    rows = load_data(in_csv)

    # Plot either a single mode or both
    modes = [args.mode] if args.mode != "both" else ["no-fog", "fog"]
    for mode in modes:
        means, stds, sizes, algos = aggregate(rows, args.metric, mode)
        plot_curves(
            means,
            stds,
            sizes,
            algos,
            metric=args.metric,
            out_dir=Path(args.out_dir),
            title=args.title,
            file_prefix=args.file_prefix,
            mode_label=mode,
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
