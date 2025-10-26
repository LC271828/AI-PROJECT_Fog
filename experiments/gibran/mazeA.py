import pygame
import sys
from heapq import heappush, heappop
import math
import time

pygame.init()

# Screen setup
WIDTH, HEIGHT = 800, 600
CELL_SIZE = 40
COLS, ROWS = WIDTH // CELL_SIZE, HEIGHT // CELL_SIZE

WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("A* Maze Solver with Cost Tracking")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLUE = (0, 150, 255)
RED = (255, 0, 0)
GREY = (100, 100, 100)
YELLOW = (255, 255, 0)

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

font = pygame.font.SysFont("Arial", 20)

# Heuristic: Manhattan distance
def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

# Drawing function
def draw_maze(path=None, visited=None, cost=0, expanded=0, runtime=None):
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

    # Display cost, expanded nodes, runtime
    text_surface = font.render(
        f"Cost: {cost} | Nodes Expanded: {expanded} | Runtime: {runtime:.3f}s" if runtime else
        f"Cost: {cost} | Nodes Expanded: {expanded}",
        True, YELLOW
    )
    WINDOW.blit(text_surface, (20, HEIGHT - 30))
    pygame.display.update()

# A* Search Algorithm
def a_star():
    open_set = []
    heappush(open_set, (0, start))
    parent = {}
    g_score = {start: 0}
    visited = set()
    nodes_expanded = 0
    start_time = time.time()

    while open_set:
        _, current = heappop(open_set)
        if current == goal:
            # reconstruct path
            path = []
            while current != start:
                path.append(current)
                current = parent[current]
            path.reverse()
            total_cost = g_score[goal]
            runtime = time.time() - start_time
            return path, visited, total_cost, nodes_expanded, runtime

        if current in visited:
            continue
        visited.add(current)
        nodes_expanded += 1

        draw_maze(visited=visited, expanded=nodes_expanded)
        pygame.time.delay(25)

        r, c = current
        for dr, dc in [(1,0),(-1,0),(0,1),(0,-1)]:
            nr, nc = r + dr, c + dc
            neighbor = (nr, nc)
            if (0 <= nr < len(maze) and 0 <= nc < len(maze[0]) and maze[nr][nc] == 0):
                temp_g = g_score[current] + 1
                if neighbor not in g_score or temp_g < g_score[neighbor]:
                    g_score[neighbor] = temp_g
                    f_score = temp_g + heuristic(neighbor, goal)
                    heappush(open_set, (f_score, neighbor))
                    parent[neighbor] = current

    runtime = time.time() - start_time
    return None, visited, 0, nodes_expanded, runtime

# Main loop
def main():
    run = True
    path, visited = [], []
    total_cost = 0
    nodes_expanded = 0
    runtime = 0
    solved = False

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if not solved:
                    path, visited, total_cost, nodes_expanded, runtime = a_star()
                    draw_maze(path, visited, total_cost, nodes_expanded, runtime)
                    solved = True

        draw_maze(path, visited, total_cost, nodes_expanded, runtime)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
