from pathlib import Path
import argparse
from src.grid import Grid
from src.agent import OnlineAgent
from src.search import astar_neighbors as astar
from src.search import astar_neighbors_with_stats as astar_with_stats  # Leo: optional stats


def main():
    # Leo: simple arg to toggle stats-enabled search
    parser = argparse.ArgumentParser(description="Demo OnlineAgent (A*). Use --with-stats to collect metrics.")
    parser.add_argument("--with-stats", action="store_true", help="Use stats-enabled A* wrapper")
    parser.add_argument("--no-fog", action="store_true", help="Disable fog (full map)")
    args = parser.parse_args()

    # Running as a module keeps repo root on sys.path. This also works if you run
    # `python examples/demo_agent.py` from repo root.
    repo_root = Path(__file__).resolve().parents[1]
    demo_map = repo_root / "maps" / "demo.csv"

    g = Grid.from_csv(demo_map)

    search_fn = astar_with_stats if args.with_stats else astar
    agent = OnlineAgent(g, full_map=bool(args.no_fog), search_algo=search_fn)
    metrics = agent.run(1000)
    print(metrics)


if __name__ == "__main__":
    main()
