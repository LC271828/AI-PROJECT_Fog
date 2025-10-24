from __future__ import annotations

import argparse
import time
from pathlib import Path
from typing import Iterable, Tuple, List

from src.grid import Grid
from src.agent import OnlineAgent
from src.search import ALGORITHMS_NEIGHBORS as SEARCH_ALGOS

Coord = Tuple[int, int]


def render_masked(grid: Grid, agent_pos: Coord | None = None, plan: List[Coord] | None = None) -> str:
    """Render the grid with fog mask. Hidden cells are '?'.
    Visible walls as '#', free as '.', start 'S', goal 'G'.
    Agent '@' overlay; planned path '*' overlay (excluding current).
    """
    lines: List[str] = []
    plan_set = set(plan[1:] if plan else [])  # exclude current position from plan overlay
    for r in range(grid.height):
        row_chars: List[str] = []
        for c in range(grid.width):
            ch = '?'
            if grid.is_visible(r, c):
                sym = grid.tile_at(r, c)
                if sym == '1':
                    ch = '#'
                elif sym == '0':
                    ch = '.'
                elif sym == 'S':
                    ch = 'S'
                elif sym == 'G':
                    ch = 'G'
                else:
                    ch = sym
            if agent_pos and (r, c) == agent_pos:
                ch = '@'
            elif (r, c) in plan_set:
                # don't overwrite agent; show next planned steps
                if ch not in ('@', 'S', 'G'):
                    ch = '*'
            row_chars.append(str(ch))
        lines.append(''.join(row_chars))
    return '\n'.join(lines)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Text visualization for Fog Maze agent")
    p.add_argument("--map", dest="map_path", type=str, default="maps/demo.csv")
    p.add_argument("--algo", choices=sorted(SEARCH_ALGOS.keys()), default="astar")
    p.add_argument("--steps", type=int, default=50, help="Number of steps to simulate")
    p.add_argument("--delay", type=float, default=0.25, help="Delay between frames (seconds)")
    p.add_argument("--no-fog", dest="no_fog", action="store_true", help="Disable fog (full map)")
    return p


def main() -> None:
    args = build_parser().parse_args()

    map_path = Path(args.map_path)
    if not map_path.exists():
        raise SystemExit(f"Map not found: {map_path}")

    grid = Grid.from_csv(map_path)
    search_fn = SEARCH_ALGOS[args.algo]

    full_map = bool(args.no_fog)
    agent = OnlineAgent(grid, full_map=full_map, search_algo=search_fn)

    print(f"Algo={args.algo} | full_map={full_map} | steps={args.steps} | delay={args.delay}s")
    print("Initial state (after initial reveal if fogged):")
    print(render_masked(grid, agent.current, getattr(agent, "current_plan", None)))
    print("\n---\n")

    for i in range(args.steps):
        cont = agent.step()
        print(f"Step {i+1}: pos={agent.current} plan_len={len(getattr(agent, 'current_plan', []) or [])}")
        print(render_masked(grid, agent.current, getattr(agent, "current_plan", None)))
        print("\n---\n")
        time.sleep(max(0.0, args.delay))
        if not cont:
            break

    m = agent.run(0)  # finalize metrics without extra steps
    print("Final metrics:")
    print(f"reached_goal={m.reached_goal} steps={m.steps} replans={m.replans} cost={m.cost}")


if __name__ == "__main__":
    main()
