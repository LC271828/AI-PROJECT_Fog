import pygame
import sys
import time  # for runtime measurement
from collections import deque

pygame.init()

# Screen setup
WIDTH, HEIGHT = 800, 600
CELL_SIZE = 40
COLS, ROWS = WIDTH // CELL_SIZE, HEIGHT // CELL_SIZE

WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Maze DFS Solver with Counter")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLUE = (0, 150, 255)
RED = (255, 0, 0)
GREY = (30, 30, 30)
YELLOW = (255, 255, 0)

# Maze layout (1 = wall, 0 = path)
maze = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,0,0,0,1,0,0,0,0,0,1,0,0,0,1,0,0,0,0,1],
    [1,0,1,0,1,0,1,1,1,0,1,0,1,0,1,1,1,1,0,1],
    [1,0,1,0,0,0,0,0,1,0,0,0,1,0,0,0,0,1,0,1],
    [1,0,1,1,1,1,1,0,1,1,1,0,1,1,1,1,0,1,0,1],
    [1,0,0,0,0,0,1,0,0,0,1,0,0,0,0,1,0,1,0,1],
    [1,1,1,1,1,0,1,1,1,0,1,1,1,1,0,1,0,1,0,1],
    [1,0,0,0,1,0,0,0,0,0,0,0,0,1,0,1,0,0,0,1],
    [1,0,1,0,1,1,1,1,1,1,1,1,0,1,0,1,1,1,0,1],
    [1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
]

start = (1, 1)
goal = (9, 18)

def draw_maze(path=None, visited=None, stats_text=None):
    """Draw the maze and optional overlays."""
    for r in range(len(maze)):
        for c in range(len(maze[0])):
            color = WHITE if maze[r][c] == 0 else BLACK
            pygame.draw.rect(WINDOW, color, (c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE - 1, CELL_SIZE - 1))

    if visited:
        for (r, c) in visited:
            pygame.draw.rect(WINDOW, GREY, (c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE - 1, CELL_SIZE - 1))

    if path:
        for (r, c) in path:
            pygame.draw.rect(WINDOW, BLUE, (c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE - 1, CELL_SIZE - 1))

    pygame.draw.rect(WINDOW, GREEN, (start[1]*CELL_SIZE, start[0]*CELL_SIZE, CELL_SIZE - 1, CELL_SIZE - 1))
    pygame.draw.rect(WINDOW, RED, (goal[1]*CELL_SIZE, goal[0]*CELL_SIZE, CELL_SIZE - 1, CELL_SIZE - 1))

    # Display stats
    if stats_text:
        font = pygame.font.SysFont("consolas", 20)
        text_surface = font.render(stats_text, True, YELLOW)
        WINDOW.blit(text_surface, (20, HEIGHT - 30))

    pygame.display.update()

def dfs_solve():
    """Solve maze with DFS and record performance metrics."""
    stack = [start]
    visited = set()
    parent = {}

    start_time = time.time()  # start timer
    nodes_expanded = 0

    while stack:
        current = stack.pop()
        nodes_expanded += 1

        if current == goal:
            end_time = time.time()
            path = []
            while current != start:
                path.append(current)
                current = parent[current]
            path.reverse()

            runtime = end_time - start_time
            cost = len(path)

            return path, visited, cost, nodes_expanded, runtime

        if current in visited:
            continue
        visited.add(current)

        draw_maze(visited=visited)
        pygame.time.delay(50)

        r, c = current
        for dr, dc in [(1,0),(-1,0),(0,1),(0,-1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < len(maze) and 0 <= nc < len(maze[0]) and maze[nr][nc] == 0 and (nr, nc) not in visited:
                parent[(nr, nc)] = current
                stack.append((nr, nc))

    end_time = time.time()
    return None, visited, 0, nodes_expanded, end_time - start_time

def main():
    run = True
    solved = False
    path = []
    visited = []
    stats_text = ""

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and not solved:
                path, visited, cost, nodes, runtime = dfs_solve()
                stats_text = f"Cost: {cost} | Nodes Expanded: {nodes} | Runtime: {runtime:.3f}s"
                draw_maze(path, visited, stats_text)
                solved = True

        draw_maze(path, visited, stats_text)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
