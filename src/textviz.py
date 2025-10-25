"""Text visualization utilities (official, testable).

Provides:
- render_masked(grid, agent_pos, plan): returns an ASCII view with fog and overlays.
- run_text_session(map_path, algo_name, steps, delay, full_map, with_stats): prints a
  step-by-step session similar to examples.visualize_text but under src/ for official use.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Tuple, Optional
import time

from src.grid import Grid
from src.agent import OnlineAgent
from src.search import ALGORITHMS_NEIGHBORS as SEARCH_ALGOS
from src.search import ALGORITHMS_NEIGHBORS_WITH_STATS as SEARCH_ALGOS_WITH_STATS

Coord = Tuple[int, int]


def render_masked(grid: Grid, agent_pos: Optional[Coord] = None, plan: Optional[List[Coord]] = None) -> str:
    """Render the grid with fog mask and overlays.

    Hidden cells are '?'. Visible walls as '#', free as '.', start 'S', goal 'G'.
    Overlays: agent '@'; plan '*' (excluding current position).
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
                if ch not in ('@', 'S', 'G'):
                    ch = '*'
            row_chars.append(str(ch))
        lines.append(''.join(row_chars))
    return '\n'.join(lines)


def run_text_session(
    map_path: Path,
    algo_name: str = "astar",
    steps: int = 50,
    delay: float = 0.25,
    full_map: bool = False,
    with_stats: bool = False,
) -> None:
    """Run a step-by-step text visualization session and print frames.

    Mirrors examples.visualize_text behavior but lives under src/ for official usage and tests.
    """
    if not map_path.exists():
        raise FileNotFoundError(f"Map not found: {map_path}")

    grid = Grid.from_csv(map_path)
    search_fn = (SEARCH_ALGOS_WITH_STATS.get(algo_name) if with_stats else SEARCH_ALGOS.get(algo_name))
    if search_fn is None:
        raise ValueError(f"Unknown algorithm '{algo_name}'")

    agent = OnlineAgent(grid, full_map=full_map, search_algo=search_fn)

    print(
        f"Algo={algo_name} | with_stats={with_stats} | full_map={full_map} | steps={steps} | delay={delay}s"
    )
    print("Initial state (after initial reveal if fogged):")
    print(render_masked(grid, agent.current, getattr(agent, "current_plan", None)))
    print("\n---\n")

    for i in range(steps):
        cont = agent.step()
        print(
            f"Step {i+1}: pos={agent.current} plan_len={len(getattr(agent, 'current_plan', []) or [])}"
        )
        print(render_masked(grid, agent.current, getattr(agent, "current_plan", None)))
        print("\n---\n")
        time.sleep(max(0.0, delay))
        if not cont:
            break

    m = agent.run(0)  # finalize metrics without extra steps
    print("Final metrics:")
    print(f"reached_goal={m.reached_goal} steps={m.steps} replans={m.replans} cost={m.cost}")
