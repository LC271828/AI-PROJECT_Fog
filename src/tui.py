"""Simple terminal UI (TUI) for choosing GUI vs Text run, map, algorithm, and options.

Designed to be invoked from src.main when no flags are provided and stdin is a TTY.
"""

from __future__ import annotations

from pathlib import Path
from typing import List

from src.search import ALGORITHMS_NEIGHBORS as SEARCH_ALGOS
from src.textviz import run_text_session


def _prompt_choice(prompt: str, choices: List[str], default_index: int = 0) -> int:
    """Prompt the user to pick an item from a numbered list.

    Returns the selected index (0-based). Falls back to ``default_index`` on
    empty input or invalid values.
    """
    for i, item in enumerate(choices):
        print(f"  [{i+1}] {item}")
    raw = input(f"{prompt} [default {default_index+1}]: ").strip()
    if not raw:
        return default_index
    try:
        idx = int(raw) - 1
        if 0 <= idx < len(choices):
            return idx
    except Exception:
        pass
    print("Invalid choice; using default.")
    return default_index


def _prompt_yes_no(prompt: str, default_yes: bool = True) -> bool:
    """Prompt for a yes/no answer, respecting a default option.

    Returns True for yes, False for no. Empty input picks the default.
    """
    if default_yes:
        d = "Y/n"
    else:
        d = "y/N"
    raw = input(f"{prompt} ({d}): ").strip().lower()
    if not raw:
        return default_yes
    return raw in ("y", "yes")


def _prompt_number(prompt: str, default, cast):
    """Prompt for a number and cast it to the desired type.

    If casting fails or input is empty, returns the provided default.
    """
    raw = input(f"{prompt} [default {default}]: ").strip()
    if not raw:
        return default
    try:
        return cast(raw)
    except Exception:
        print("Invalid input; using default.")
        return default


def run_interactive() -> int:
    """Interactive terminal menu for GUI or Text runs.

    Behavior
    - If GUI is selected, tries to launch the pygame menu; falls back to Text
      when pygame is unavailable.
    - In Text mode, guides the user through choosing map, algorithm, stats,
      fog on/off, steps, and delay; then runs a text session.
    Returns process-like exit code (0 for success, nonzero for failure).
    """
    # Mode choice prompt
    print("Fog Maze — choose mode:\n  [1] GUI (pygame)\n  [2] Text (ASCII)")
    raw = input("Select mode [default 1]: ").strip()
    if raw and raw not in ("1", "2"):
        print("Invalid input; defaulting to GUI.")
        raw = "1"
    if not raw:
        raw = "1"

    if raw == "1":
        # Try GUI (pygame)
        try:
            from src.visualize import run_menu
            run_menu()
            return 0
        except Exception:
            # If pygame is not installed or fails to init, fall back to Text mode.
            print("GUI unavailable; falling back to Text mode.")

    # Text mode flow ---------------------------------------------------------
    # Discover maps
    map_dir = Path("maps")
    maps = sorted([p for p in map_dir.glob("*.csv")])
    map_names = [p.name for p in maps] or ["(no maps found)"]
    if not maps:
        print("No maps found in maps/; cannot run text mode.")
        return 2

    print("Select a map:")
    mi = _prompt_choice("Map", map_names, default_index=0)
    chosen_map = maps[mi]

    algos = sorted(list(SEARCH_ALGOS.keys())) or ["astar"]
    print("Select an algorithm:")
    if "astar" in algos:
        default_algo_index = algos.index("astar")
    else:
        default_algo_index = 0
    ai = _prompt_choice("Algorithm", algos, default_index=default_algo_index)
    algo_name = algos[ai]

    # Run configuration
    with_stats = _prompt_yes_no("Collect with-stats metrics?", default_yes=True)
    full_map = not _prompt_yes_no("Enable fog?", default_yes=True)  # fog => not full_map
    steps = _prompt_number("Steps to simulate", 60, int)
    delay = _prompt_number("Delay between frames (seconds)", 0.1, float)

    # Execute text session
    run_text_session(
        chosen_map,
        algo_name=algo_name,
        steps=steps,
        delay=delay,
        full_map=full_map,
        with_stats=with_stats,
    )
    return 0
