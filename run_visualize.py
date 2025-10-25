from src.grid import Grid
from src.agent import OnlineAgent
from src.search import ALGORITHMS_NEIGHBORS as SEARCH_ALGOS
from src.visualize import visualize


def main():
    grid = Grid.from_csv('maps/demo.csv')
    search_fn = SEARCH_ALGOS.get('ucs')
    agent = OnlineAgent(grid, full_map=False, search_algo=search_fn)
    visualize(agent, grid, cell_size=24, fps=8)


if __name__ == '__main__':
    main()
