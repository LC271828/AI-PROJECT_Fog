from src.grid import Grid
from pathlib import Path


def main():
    # Running as a module keeps repo root on sys.path. This also works if you run
    # `python examples/demo_grid.py` from repo root.
    repo_root = Path(__file__).resolve().parents[1]
    demo_map = repo_root / "maps" / "demo.csv"

    g = Grid()
    g.from_csv(map=demo_map)

    print("Height:", g.height)
    print("Width:", g.width)

    print("Initial visible (should be all False):")
    for row in g.visible:
        print(row)

    print("\nReveal from start:")
    g.reveal_from(g.start)
    for row in g.visible:
        print(row)

    print("\nVisible tiles:")
    print(g.visible_tiles())


if __name__ == "__main__":
    main()
