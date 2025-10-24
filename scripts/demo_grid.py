from pathlib import Path
from src.grid import Grid


def main():
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
