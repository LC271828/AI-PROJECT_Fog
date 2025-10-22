import pygame
import sys
import time
from collections import deque

pygame.init()

# Screen setup
WIDTH, HEIGHT = 800, 600
CELL_SIZE = 40
COLS, ROWS = WIDTH // CELL_SIZE, HEIGHT // CELL_SIZE

WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("BFS Maze Solver with Cost Tracking")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLUE = (0, 150, 255)
RED = (255, 0, 0)
GREY = (50, 50, 50)
YELLOW = (255, 255, 0)

# Font
font = pygame.font.SysFont("arial", 22, bold=True)

# Maze layout (1 = wall, 0 = path)
maze = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,0,0,0,1,0,0,0,0,0,1,0,0,0,1,0,0,0,0,1],
    [1,0,1,0,1,0,1,1,1,0,1,0,1,0,1,1,1,1,0,1],
    [1,0,1,0,0,0,0,0,1,0,0,0,1,0,0,0,0,1,0,1],
    [1,0,1,1,1,1,1,0,1,1,1,0,1,1,1,1,0,1,0,1],
    [1,0,0,0,0,0,1,0,0,0,1,0,0,0,0,1,0,1,0,1],
    [1,0,1,1,1,0,1,1,1,0,1,1,1,1,0,1,0,1,0,1],
    [1,0,0,0,1,0,0,0,0,0,0,0,0,1,0,1,0,0,0,1],
    [1,0,1,0,1,1,1,1,1,1,1,1,0,1,0,1,1,1,0,1],
    [1,0,1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
]

start = (1, 1)
goal = (9, 18)

def draw_maze(path=None, visited=None, cost=None, nodes_expanded=None, runtime=None):
    """Draw the maze grid with optional path, visited highlighting, and stats."""
    WINDOW.fill(BLACK)
    
    for r in range(len(maze)):
        for c in range(len(maze[0])):
            color = WHITE if maze[r][c] == 0 else BLACK
            pygame.draw.rect(WINDOW, color, (c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE-1, CELL_SIZE-1))
    if visited:
        for (r, c) in visited:
            pygame.draw.rect(WINDOW, GREY, (c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE-1, CELL_SIZE-1))
    if path:
        for (r, c) in path:
            pygame.draw.rect(WINDOW, BLUE, (c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE-1, CELL_SIZE-1))
    pygame.draw.rect(WINDOW, GREEN, (start[1]*CELL_SIZE, start[0]*CELL_SIZE, CELL_SIZE-1, CELL_SIZE-1))
    pygame.draw.rect(WINDOW, RED, (goal[1]*CELL_SIZE, goal[0]*CELL_SIZE, CELL_SIZE-1, CELL_SIZE-1))

    # ✅ Draw statistics text
    if cost is not None and nodes_expanded is not None and runtime is not None:
        stats_text = f"Cost: {cost} | Nodes Expanded: {nodes_expanded} | Runtime: {runtime:.3f}s"
        text_surface = font.render(stats_text, True, YELLOW)
        WINDOW.blit(text_surface, (20, HEIGHT - 30))

    pygame.display.update()

def bfs_solve():
    """Solve the maze using Breadth-First Search (shortest path)."""
    queue = deque([start])
    visited = set()
    parent = {}

    cost = 0
    nodes_expanded = 0

    start_time = time.time()

    while queue:
        current = queue.popleft()
        nodes_expanded += 1

        if current == goal:
            path = []
            while current != start:
                path.append(current)
                current = parent[current]
                cost += 1
            path.reverse()

            end_time = time.time()
            runtime = end_time - start_time

            print(f"✅ BFS Finished")
            print(f"Cost: {cost} | Nodes Expanded: {nodes_expanded} | Runtime: {runtime:.3f}s")

            return path, visited, cost, nodes_expanded, runtime

        if current in visited:
            continue
        visited.add(current)

        # visualize visited nodes
        draw_maze(visited=visited)
        pygame.time.delay(20)

        r, c = current
        for dr, dc in [(1,0),(-1,0),(0,1),(0,-1)]:
            nr, nc = r + dr, c + dc
            if (0 <= nr < len(maze) and 0 <= nc < len(maze[0]) and 
                maze[nr][nc] == 0 and (nr, nc) not in visited and (nr, nc) not in queue):
                parent[(nr, nc)] = current
                queue.append((nr, nc))

    print("❌ No path found.")
    return None, visited, cost, nodes_expanded, 0

def main():
    run = True
    path, visited = [], []
    solved = False
    cost = nodes_expanded = 0
    runtime = 0

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if not solved:
                    path, visited, cost, nodes_expanded, runtime = bfs_solve()
                    draw_maze(path, visited, cost, nodes_expanded, runtime)
                    solved = True

        draw_maze(path, visited, cost, nodes_expanded, runtime)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
