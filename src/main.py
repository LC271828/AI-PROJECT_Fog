"""Minimal headless CLI entry point.

Aligns with TEAM_API and README: loads config.json defaults, overrides via CLI flags,
constructs Grid and OnlineAgent, runs, and prints metrics. GUI is optional and not
implemented yet (flag is accepted and noted).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.grid import Grid
from src.agent import OnlineAgent
from src.search import ALGORITHMS_NEIGHBORS as SEARCH_ALGOS
# Leo: allow opting into with-stats search wrappers
from src.search import ALGORITHMS_NEIGHBORS_WITH_STATS as SEARCH_ALGOS_WITH_STATS


def load_config(path: Path) -> dict:
	"""Load JSON config; return {} if missing or invalid."""
	try:
		text = Path(path).read_text(encoding="utf-8")
		cfg = json.loads(text)
		if not isinstance(cfg, dict):
			return {}
		return cfg
	except FileNotFoundError:
		return {}
	except Exception:
		# Keep CLI resilient; ignore malformed config
		return {}


def build_parser() -> argparse.ArgumentParser:
	"""Construct the CLI argument parser.

	Flags
	- --config: JSON config path (defaults used if missing)
	- --map: CSV map path
	- --algo: search algorithm name (bfs/dfs/ucs/astar [+ optional experimental like greedy])
	- --gui: accept flag but GUI not implemented yet
	- --no-fog/--fog: toggle fog; defaults based on config fog_radius
	- --max-steps: cap number of agent steps
	"""
	p = argparse.ArgumentParser(prog="python -m src.main", description="Fog Maze")
	p.add_argument("--config", type=str, default="config.json", help="Path to JSON config (default: config.json)")
	p.add_argument("--map", dest="map_path", type=str, help="Path to CSV map (overrides config)")
	# Algorithm choices are taken from the core mapping (includes bfs/dfs/ucs/astar/greedy)
	_all_algos = sorted(SEARCH_ALGOS.keys())
	p.add_argument("--algo", choices=_all_algos, help="Search algorithm (overrides config)")
	p.add_argument("--with-stats", dest="with_stats", action="store_true", help="Use metrics-enabled search variant (nodes expanded, runtime, cost)")
	p.add_argument("--gui", action="store_true", help="Launch GUI visualizer (requires pygame). If no flags are given, we try GUI by default.")
	fog_group = p.add_mutually_exclusive_group()
	fog_group.add_argument("--no-fog", dest="no_fog", action="store_true", help="Disable fog (agent has full map)")
	fog_group.add_argument("--fog", dest="fog", action="store_true", help="Enable fog (default if config sets fog_radius > 0)")
	p.add_argument("--max-steps", type=int, default=10000, help="Max steps for the agent (default: 10000)")
	return p


def main(argv: list[str] | None = None) -> int:
	parser = build_parser()
	args = parser.parse_args(argv)

	# Load defaults from config.json
	cfg = load_config(Path(args.config))
    
	# Decide default mode: if user gave no specific flags, prefer GUI when available.
	user_specified_mode = any([
		args.gui,
		args.with_stats,
		bool(args.map_path),
		bool(args.algo),
		args.no_fog,
		args.fog,
	])

	if not user_specified_mode:
		# If interactive TTY: present a small TUI to choose GUI or Text. Else, try GUI.
		try:
			if sys.stdin.isatty():
				from src.tui import run_interactive
				return run_interactive()
			else:
				from src.visualize import run_menu  # lazy import; raises if pygame missing
				run_menu()
				return 0
		except Exception:
			# Fall back to headless without failing; continue to construct Grid/Agent below.
			print("Note: GUI/TUI not available. Falling back to headless CLI.")
	# Resolve map
	map_path = Path(args.map_path or cfg.get("map", "maps/demo.csv"))
	if not map_path.exists():
		print(f"Error: map not found: {map_path}", file=sys.stderr)
		return 2

	# Resolve algo
	algo_name = args.algo or cfg.get("algo", "astar")
	if algo_name not in SEARCH_ALGOS:
		print(f"Error: unknown --algo '{algo_name}'. Choose one of: {', '.join(sorted(SEARCH_ALGOS.keys()))}", file=sys.stderr)
		return 2
	# Leo: Choose stats-enabled wrapper when requested
	if args.with_stats:
		search_fn = SEARCH_ALGOS_WITH_STATS.get(algo_name)
	else:
		search_fn = SEARCH_ALGOS.get(algo_name)

	# Resolve fog vs full_map
	# If --no-fog given => full_map=True
	# Else if --fog flag given OR config fog_radius>0 => fog enabled => full_map=False
	cfg_fog_radius = int(cfg.get("fog_radius", 1)) if isinstance(cfg.get("fog_radius", 1), (int, float, str)) else 1
	fog_enabled = False
	if args.no_fog:
		fog_enabled = False
	elif args.fog:
		fog_enabled = True
	else:
		fog_enabled = cfg_fog_radius > 0
	full_map = not fog_enabled

	# GUI mode (optional). If requested either via flag or config, launch the GUI and return.
	if args.gui or cfg.get("gui", False):
		try:
			from src.visualize import run_menu  # lazy import; visualize handles pygame optionality
		except Exception as e:
			print(
				"Error: GUI requested but could not import visualizer.\n"
				"Install pygame via:\n  powershell -ExecutionPolicy Bypass -File .\\scripts\\setup.ps1 -WithGUI",
				file=sys.stderr,
			)
			return 2
		# Launch menu (blocks until exit), then return 0
		run_menu()
		return 0

	# Construct Grid and Agent
	try:
		grid = Grid.from_csv(map_path)
	except Exception as e:
		print(f"Error: failed to load map: {e}", file=sys.stderr)
		return 2

	agent = OnlineAgent(grid, full_map=full_map, search_algo=search_fn)

	# Run
	metrics = agent.run(max_steps=args.max_steps)

	# Print metrics
	print("Start:", metrics.start)
	print("Goal:", metrics.goal)
	print("Reached goal:", metrics.reached_goal)
	print("Steps:", metrics.steps)
	print("Replans:", metrics.replans)
	print("Nodes expanded:", metrics.nodes_expanded)
	print("Cost:", metrics.cost)
	print("Runtime (s):", f"{metrics.runtime:.6f}")
	print("Path length:", len(metrics.path_taken) if metrics.path_taken else 0)

	return 0


if __name__ == "__main__":
	raise SystemExit(main())
