from pathlib import Path
from src.grid import Grid
from src.agent import OnlineAgent
from src.search import astar_neighbors as astar


def main():
    repo_root = Path(__file__).resolve().parents[1]
    demo_map = repo_root / "maps" / "demo.csv"

    # CHANGE: Use TEAM_API classmethod constructor for consistency with examples and docs
    g = Grid.from_csv(demo_map)

    agent = OnlineAgent(g, full_map=False, search_algo=astar)
    metrics = agent.run(1000)
    print(metrics)


if __name__ == "__main__":
    main()
