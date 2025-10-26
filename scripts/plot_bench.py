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
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple


def _parse_args(argv: List[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Plot benchmark CSV from scripts.bench")
    p.add_argument("--in", dest="input_csv", required=False, default=None, help="Input CSV path from scripts.bench")
    p.add_argument("--out", dest="out_dir", default="reports/plots", help="Output directory for plots")
    p.add_argument("--metric", choices=["runtime", "cost"], default="runtime", help="Metric to plot: runtime or cost")
    p.add_argument("--mode", choices=["fog", "no-fog", "both"], default="no-fog", help="Filter mode to plot")
    p.add_argument("--title", default=None, help="Optional plot title")
    p.add_argument("--file-prefix", default=None, help="Optional prefix for output filenames")
    p.add_argument("-i", "--interactive", action="store_true", help="Interactive terminal prompts to choose options")
    # Presentation/clarity options
    p.add_argument("--style", choices=["overlay", "facet", "delta-bfs"], default="overlay", help="Visualization style: overlay lines (default), small multiples (facet), or difference vs BFS (delta-bfs)")
    p.add_argument("--logy", action="store_true", help="Use logarithmic y-scale (useful for runtime)")
    p.add_argument("--no-errorbars", dest="errorbars", action="store_false", help="Disable error bars for cleaner lines")
    p.add_argument("--no-annotate", dest="annotate", action="store_false", help="Disable end-of-line labels")
    p.add_argument("--label-sep-px", type=int, default=6, help="Vertical pixel separation between end labels when annotating")
    p.add_argument("--no-jitter", dest="jitter", action="store_false", help="Disable small x-offset per algorithm to reduce overlap of markers")
    # Theoretical overlays
    p.add_argument(
        "--big-o",
        dest="big_o",
        action="append",
        choices=["n", "nlogn", "n2", "logn"],
        help="Overlay one or more Big-O curves fitted to a base algorithm (can be repeated).",
    )
    p.add_argument("--big-o-base", dest="big_o_base", default="bfs", help="Algorithm to fit Big-O constant to (default: bfs)")
    p.add_argument("--big-o-color", dest="big_o_color", default="#444", help="Color for Big-O overlays")
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


# -------- Interactive helpers --------
def _pick(label: str, choices: List[str], default_idx: int = 0) -> str:
    print(f"\n{label}")
    for i, c in enumerate(choices):
        dmark = " (default)" if i == default_idx else ""
        print(f"  [{i+1}] {c}{dmark}")
    raw = input(f"Choose 1-{len(choices)} [default {default_idx+1}]: ").strip()
    if not raw:
        return choices[default_idx]
    try:
        idx = int(raw) - 1
        if 0 <= idx < len(choices):
            return choices[idx]
    except Exception:
        pass
    return choices[default_idx]


def _yesno(label: str, default: bool = True) -> bool:
    d = "Y/n" if default else "y/N"
    raw = input(f"{label} [{d}]: ").strip().lower()
    if not raw:
        return default
    return raw in ("y", "yes")


def _prompt_str(label: str, default: str | None = None) -> str | None:
    d = f" (default: {default})" if default else ""
    raw = input(f"{label}{d}: ").strip()
    return raw or default


def _prompt_multi(label: str, options: List[str], default: List[str] | None = None) -> List[str]:
    default = default or []
    print(f"\n{label}")
    for i, o in enumerate(options):
        dmark = " (default)" if o in default else ""
        print(f"  [{i+1}] {o}{dmark}")
    raw = input("Enter comma-separated numbers, or blank for defaults: ").strip()
    if not raw:
        return list(default)
    picks: List[str] = []
    for part in raw.split(','):
        part = part.strip()
        if not part:
            continue
        try:
            idx = int(part) - 1
            if 0 <= idx < len(options):
                picks.append(options[idx])
        except Exception:
            pass
    return picks


def _interactive_fill(args: argparse.Namespace) -> argparse.Namespace:
    # Discover CSVs in reports/
    candidates: List[Path] = []
    reports = Path("reports")
    if reports.exists():
        candidates.extend(sorted(reports.glob("*.csv"), key=lambda p: p.stat().st_mtime, reverse=True))
    # Build menu
    menu = [str(p) for p in candidates]
    menu.append("Enter a path manually…")
    choice = _pick("Select input CSV", menu, default_idx=0 if candidates else 0)
    if choice.startswith("Enter"):
        manual = _prompt_str("Path to CSV", args.input_csv)
        args.input_csv = manual or args.input_csv
    else:
        args.input_csv = choice

    args.mode = _pick("Mode", ["no-fog", "fog", "both"], default_idx=1 if "fog" in str(args.input_csv) else 0)
    args.metric = _pick("Metric", ["runtime", "cost"], default_idx=0)
    args.style = _pick("Style", ["overlay", "facet", "delta-bfs"], default_idx=0)
    args.logy = _yesno("Use log scale on y?", default=False)
    args.errorbars = _yesno("Show error bars?", default=True)
    args.annotate = _yesno("Annotate end-of-line labels?", default=True)
    args.jitter = _yesno("Jitter markers to reduce overlap?", default=True)
    sep = _prompt_str("End label vertical separation (px)", str(getattr(args, "label_sep_px", 10)))
    try:
        args.label_sep_px = int(sep) if sep is not None else 10
    except Exception:
        args.label_sep_px = 10
    # Big-O overlays
    if _yesno("Add Big-O overlays?", default=False):
        args.big_o = _prompt_multi("Choose overlays", ["n", "nlogn", "n2", "logn"], default=["n", "nlogn"]) or []
        args.big_o_base = _prompt_str("Fit overlays to which algorithm?", getattr(args, "big_o_base", "bfs")) or "bfs"
    else:
        args.big_o = []
    args.out_dir = _prompt_str("Output folder", getattr(args, "out_dir", "reports/plots")) or "reports/plots"
    args.file_prefix = _prompt_str("Optional file prefix (blank to auto)", getattr(args, "file_prefix", None))
    args.title = _prompt_str("Optional title (blank to auto)", getattr(args, "title", None))
    # Show summary and confirm
    print("\nSummary:")
    print(f"  CSV:        {args.input_csv}")
    print(f"  Mode:       {args.mode}")
    print(f"  Metric:     {args.metric}")
    print(f"  Style:      {args.style}")
    print(f"  Log y:      {bool(args.logy)}")
    print(f"  Errorbars:  {bool(args.errorbars)}")
    print(f"  Annotate:   {bool(args.annotate)}  (sep {getattr(args, 'label_sep_px', 10)} px)")
    print(f"  Jitter:     {bool(args.jitter)}")
    print(f"  Big-O:      {', '.join(getattr(args, 'big_o', []) or []) or 'None'}  (base {getattr(args, 'big_o_base', 'bfs')})")
    print(f"  Out dir:    {args.out_dir}")
    print(f"  File prefix:{' ' + args.file_prefix if args.file_prefix else ' <auto>'}")
    print(f"  Title:      {' ' + args.title if args.title else ' <auto>'}")
    if not _yesno("Proceed?", default=True):
        raise SystemExit(0)
    return args


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


def _algo_styles(algos: List[str]):
    """Return per-algorithm (color/marker/linestyle) cycling deterministically."""
    # Matplotlib default color cycle is fine; just pick distinct markers/linestyles
    markers = ["o", "s", "^", "D", "P", "X", "v", "+", "*"]
    linestyles = ["-", "--", "-.", ":"]
    styles = {}
    for i, a in enumerate(sorted(algos)):
        styles[a] = {
            "marker": markers[i % len(markers)],
            "linestyle": linestyles[i % len(linestyles)],
        }
    return styles


def _x_offsets(sizes: List[int], algos: List[str]) -> Dict[str, List[float]]:
    """Compute small x-jitter per algorithm to reduce marker overlap.

    Offsets are a small fraction of the minimum gap between consecutive sizes.
    If only one size is present, use a tiny constant offset.
    """
    if len(sizes) <= 1:
        base = 0.2
    else:
        gaps = [abs(b - a) for a, b in zip(sizes, sizes[1:]) if b is not None]
        base = (min(gaps) if gaps else 1) * 0.06
    k = len(algos)
    # Center offsets around 0, e.g., for k=5 -> [-2,-1,0,1,2]*base/k
    centers = [i - (k - 1) / 2.0 for i in range(k)]
    per_algo = {}
    for idx, a in enumerate(algos):
        per_algo[a] = [sizes[j] + (centers[idx] * base) for j in range(len(sizes))]
    return per_algo


def _annotate_line_end(ax, xs, ys, label, offset=(5, 0)):
    # Find last finite point
    import math
    for x, y in zip(reversed(xs), reversed(ys)):
        if y is not None and not math.isnan(y):
            ax.annotate(label, xy=(x, y), xytext=offset, textcoords="offset points", fontsize=9, alpha=0.9)
            break


def _big_o_funcs():
    import math
    return {
        "n": lambda n: float(n),
        "nlogn": lambda n: float(n) * (math.log2(max(n, 2))),
        "n2": lambda n: float(n) ** 2,
        "logn": lambda n: math.log2(max(n, 2)),
    }


def _fit_scale(y_obs: List[float], f_vals: List[float]) -> float:
    # Best c minimizing sum (y - c f)^2 is c = sum(y f) / sum(f^2)
    num = sum(y * f for y, f in zip(y_obs, f_vals))
    den = sum(f * f for f in f_vals) or 1.0
    return num / den


def plot_curves(
    means: Dict[Tuple[str, int], float],
    stds: Dict[Tuple[str, int], float],
    sizes: List[int],
    algos: List[str],
    metric: str,
    out_dir: Path,
    title: str | None = None,
    file_prefix: str | None = None,
    mode_label: str = "",
    style: str = "overlay",
    logy: bool = False,
    errorbars: bool = True,
    annotate: bool = True,
    jitter: bool = True,
) -> Path | None:
    try:
        import matplotlib.pyplot as plt  # type: ignore
    except Exception:
        print("Matplotlib is required for plotting. Install with: python -m pip install matplotlib")
        return None

    metric_label = "Average Runtime (s)" if metric == "runtime" else "Average Cost (steps)"
    styles = _algo_styles(algos)

    if style == "facet":
        # Small multiples: one subplot per algo, shared axes
        cols = min(3, max(1, len(algos)))
        rows = (len(algos) + cols - 1) // cols
        fig, axes = plt.subplots(rows, cols, figsize=(6 * cols, 3.5 * rows), sharex=True, sharey=True)
        # Normalize axes to a flat list
        if hasattr(axes, "ravel"):
            axes_list = list(axes.ravel())
        elif isinstance(axes, (list, tuple)):
            axes_list = list(axes)
        else:
            axes_list = [axes]
        for i, algo in enumerate(algos):
            ax = axes_list[i]
            ys = [means.get((algo, n), float("nan")) for n in sizes]
            es = [stds.get((algo, n), 0.0) for n in sizes]
            xvals = sizes
            if errorbars:
                ax.errorbar(xvals, ys, yerr=es, marker=styles[algo]["marker"], linestyle=styles[algo]["linestyle"], capsize=3, label=algo)
            else:
                ax.plot(xvals, ys, marker=styles[algo]["marker"], linestyle=styles[algo]["linestyle"], label=algo)
            ax.set_title(algo)
            ax.grid(True, alpha=0.3)
            if logy:
                ax.set_yscale("log")
        # Labels on outer edges
        for ax in axes_list:
            ax.set_xlabel("Maze size (n)")
            ax.set_ylabel(metric_label)
        # Global title
        fig.suptitle(title or (f"{metric_label} vs Size ({mode_label})" if mode_label else f"{metric_label} vs Size"))
        fig.tight_layout(rect=(0.0, 0.03, 1.0, 0.95))
    elif style == "delta-bfs":
        # Plot difference from BFS as baseline to reveal subtle divergences
        fig, ax = plt.subplots(figsize=(8, 5))
        baseline = "bfs"
        if baseline not in algos:
            print("[plot] delta-bfs requested but BFS not present; falling back to overlay")
            style = "overlay"
        else:
            y0 = [means.get((baseline, n), float("nan")) for n in sizes]
            ax.axhline(0, color="#888", linewidth=1, alpha=0.7, label=f"{baseline} baseline")
            # Prepare end label staggering based on last delta value
            deltas_last = []
            for algo in algos:
                ys = [means.get((algo, n), float("nan")) for n in sizes]
                ydelta = [(a - b) if (a == a and b == b) else float("nan") for a, b in zip(ys, y0)]
                # find last finite
                import math
                last = next((v for v in reversed(ydelta) if v is not None and not math.isnan(v)), float("nan"))
                deltas_last.append((algo, last))
            # sort by value to stagger vertically
            deltas_last.sort(key=lambda t: (t[1] if t[1] == t[1] else float("inf")))
            k = len(deltas_last)
            offsets = {algo: (5, int((i - (k - 1) / 2.0) * max(1,  args_label_sep))) for i, (algo, _) in enumerate(deltas_last)}
            for algo in algos:
                ys = [means.get((algo, n), float("nan")) for n in sizes]
                # delta = algo - bfs
                ydelta = [(a - b) if (a == a and b == b) else float("nan") for a, b in zip(ys, y0)]
                xvals = sizes
                ax.plot(xvals, ydelta, marker=styles[algo]["marker"], linestyle=styles[algo]["linestyle"], label=algo)
                if annotate:
                    _annotate_line_end(ax, xvals, ydelta, algo, offset=offsets.get(algo, (5, 0)))
            ax.set_xlabel("Maze size (n)")
            ax.set_ylabel(("Δ Runtime vs BFS (s)" if metric == "runtime" else "Δ Cost vs BFS (steps)"))
            if title:
                ax.set_title(title)
            elif mode_label:
                ax.set_title(f"Difference vs BFS ({mode_label})")
            else:
                ax.set_title("Difference vs BFS")
            ax.legend(title="Algorithm", ncol=2)
            ax.grid(True, alpha=0.3)
            if logy:
                # Avoid log of zero/negative deltas; ignore logy in delta mode
                pass
            fig.tight_layout()
    elif style == "overlay":
        fig, ax = plt.subplots(figsize=(8, 5))
        # Optional jitter of x to separate markers
        xvals_map = _x_offsets(sizes, algos) if jitter else {a: sizes for a in algos}
        # Prepare end label staggering based on last y value
        lasts = []
        import math
        for algo in algos:
            ys = [means.get((algo, n), float("nan")) for n in sizes]
            last = next((v for v in reversed(ys) if v is not None and not math.isnan(v)), float("nan"))
            lasts.append((algo, last))
        lasts.sort(key=lambda t: (t[1] if t[1] == t[1] else float("inf")))
        k = len(lasts)
        # args_label_sep is provided via closure (see below).
        offsets = {algo: (5, int((i - (k - 1) / 2.0) * max(1, args_label_sep))) for i, (algo, _) in enumerate(lasts)}
        for algo in algos:
            ys = [means.get((algo, n), float("nan")) for n in sizes]
            es = [stds.get((algo, n), 0.0) for n in sizes]
            xvals = xvals_map.get(algo, sizes)
            if errorbars:
                ax.errorbar(xvals, ys, yerr=es, marker=styles[algo]["marker"], linestyle=styles[algo]["linestyle"], capsize=3, label=algo, linewidth=1.5)
            else:
                ax.plot(xvals, ys, marker=styles[algo]["marker"], linestyle=styles[algo]["linestyle"], label=algo, linewidth=1.8)
            if annotate:
                _annotate_line_end(ax, xvals, ys, algo, offset=offsets.get(algo, (5, 0)))
        ax.set_xlabel("Maze size (n)")
        ax.set_ylabel(metric_label)
        if title:
            ax.set_title(title)
        elif mode_label:
            ax.set_title(f"{metric_label} vs Size ({mode_label})")
        else:
            ax.set_title(f"{metric_label} vs Size")
        ax.legend(title="Algorithm", ncol=2)
        ax.grid(True, alpha=0.3)
        if logy:
            ax.set_yscale("log")
        # Optional Big-O overlays (fit to a base algorithm)
        try:
            big_os = []  # list of (label, x, y)
            if isinstance(getattr(plot_curves, "_big_o_models", []), list):
                models = getattr(plot_curves, "_big_o_models")  # type: ignore[attr-defined]
            else:
                models = []
            base_algo = getattr(plot_curves, "_big_o_base", "bfs")  # type: ignore[attr-defined]
            color = getattr(plot_curves, "_big_o_color", "#444")  # type: ignore[attr-defined]
            funcs = _big_o_funcs()
            if models:
                # choose base that exists
                base = base_algo if base_algo in algos else (algos[0] if algos else None)
                if base:
                    # observed y for base
                    y_obs = []
                    x_fit = []
                    for n in sizes:
                        yv = means.get((base, n))
                        if yv is not None:
                            y_obs.append(yv)
                            x_fit.append(n)
                    for m in models:
                        f = funcs.get(m)
                        if not f:
                            continue
                        f_vals = [f(n) for n in x_fit]
                        c = _fit_scale(y_obs, f_vals)
                        y_curve = [c * f(n) for n in sizes]
                        ax.plot(sizes, y_curve, linestyle=(0, (3, 3)), color=color, linewidth=1.2, label=f"O({m}) fit to {base}")
        except Exception:
            pass
        fig.tight_layout()

    # Save
    _ensure_dir(out_dir)
    stem = file_prefix or f"plot_{metric}"
    if mode_label:
        stem += f"_{mode_label.replace('-', '')}"
    if style and style != "overlay":
        stem += f"_{style.replace('-', '')}"
    # Always append date-time stamp to filename for uniqueness and traceability
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = out_dir / f"{stem}_{stamp}.png"
    fig.savefig(str(out_path), dpi=144)
    print(f"Wrote plot to {out_path}")
    return out_path


def main(argv: List[str] | None = None) -> int:
    args = _parse_args(argv)
    if getattr(args, "interactive", False):
        args = _interactive_fill(args)
    if args.input_csv is None and not getattr(args, "interactive", False):
        print("Input CSV is required (use --in) or run with --interactive to pick via prompts.")
        return 2

    # After interactive fill (if used), input_csv must be set
    if args.input_csv is None:
        print("No CSV selected.")
        return 2
    in_csv = Path(args.input_csv)
    if not in_csv.exists():
        print(f"Input CSV not found: {in_csv}")
        return 2

    rows = load_data(in_csv)

    # Plot either a single mode or both
    modes = [args.mode] if args.mode != "both" else ["no-fog", "fog"]
    for mode in modes:
        means, stds, sizes, algos = aggregate(rows, args.metric, mode)
        # Pass label separation through a tiny closure variable used above for offsets
        global args_label_sep
        args_label_sep = int(getattr(args, "label_sep_px", 6))
        # Configure static attributes for Big-O overlays to pass into plot_curves without
        # altering its signature (simple approach to keep existing calls untouched).
        setattr(plot_curves, "_big_o_models", list(getattr(args, "big_o", []) or []))
        setattr(plot_curves, "_big_o_base", str(getattr(args, "big_o_base", "bfs")))
        setattr(plot_curves, "_big_o_color", str(getattr(args, "big_o_color", "#444")))
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
            style=args.style,
            logy=bool(args.logy),
            errorbars=bool(getattr(args, "errorbars", True)),
            annotate=bool(getattr(args, "annotate", True)),
            jitter=bool(getattr(args, "jitter", True)),
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
