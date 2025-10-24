from pathlib import Path
from src.grid import Grid
from src.agent import OnlineAgent
from src.search import astar_neighbors as astar


def main():
    # Running as a module keeps repo root on sys.path. This also works if you run
    # `python examples/demo_agent.py` from repo root.
    repo_root = Path(__file__).resolve().parents[1]
    demo_map = repo_root / "maps" / "demo.csv"

    g = Grid()
    g.from_csv(map=demo_map)

    agent = OnlineAgent(g, full_map=False, search_algo=astar)
    metrics = agent.run(1000)
    print(metrics)


if __name__ == "__main__":
    main()
