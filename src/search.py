from heapq import heappush, heappop
from collections import deque

def reconstruct_path(came_from, start, goal):
    path = []
    current = goal
    while current != start:
        path.append(current)
        current = came_from.get(current)
        if current is None:
            return []
    path.append(start)
    path.reverse()
    return path


def bfs(grid, start, goal):
    """Breadth-First Search."""
    queue = deque([start])
    came_from = {}
    visited = {start}
    nodes_expanded = 0

    while queue:
        current = queue.popleft()
        nodes_expanded += 1

        if current == goal:
            return reconstruct_path(came_from, start, goal), nodes_expanded

        for neighbor in grid.neighbors(current):
            if neighbor not in visited:
                visited.add(neighbor)
                came_from[neighbor] = current
                queue.append(neighbor)

    return [], nodes_expanded


def dfs(grid, start, goal):
    """Depth-First Search."""
    stack = [start]
    came_from = {}
    visited = {start}
    nodes_expanded = 0

    while stack:
        current = stack.pop()
        nodes_expanded += 1

        if current == goal:
            return reconstruct_path(came_from, start, goal), nodes_expanded

        for neighbor in grid.neighbors(current):
            if neighbor not in visited:
                visited.add(neighbor)
                came_from[neighbor] = current
                stack.append(neighbor)

    return [], nodes_expanded


def ucs(grid, start, goal):
    """Uniform Cost Search."""
    frontier = []
    heappush(frontier, (0, start))
    came_from = {}
    cost_so_far = {start: 0}
    nodes_expanded = 0

    while frontier:
        cost, current = heappop(frontier)
        nodes_expanded += 1

        if current == goal:
            return reconstruct_path(came_from, start, goal), nodes_expanded

        for neighbor in grid.neighbors(current):
            new_cost = cost_so_far[current] + grid.cost(current, neighbor)
            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                cost_so_far[neighbor] = new_cost
                heappush(frontier, (new_cost, neighbor))
                came_from[neighbor] = current

    return [], nodes_expanded


def astar(grid, start, goal, h=lambda a, b: abs(a[0]-b[0]) + abs(a[1]-b[1])):
    """A* Search with Manhattan heuristic."""
    frontier = []
    heappush(frontier, (0, start))
    came_from = {}
    g_score = {start: 0}
    nodes_expanded = 0

    while frontier:
        _, current = heappop(frontier)
        nodes_expanded += 1

        if current == goal:
            return reconstruct_path(came_from, start, goal), nodes_expanded

        for neighbor in grid.neighbors(current):
            tentative_g = g_score[current] + grid.cost(current, neighbor)
            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                g_score[neighbor] = tentative_g
                f_score = tentative_g + h(neighbor, goal)
                heappush(frontier, (f_score, neighbor))
                came_from[neighbor] = current

    return [], nodes_expanded


ALGORITHMS = {
    "bfs": bfs,
    "dfs": dfs,
    "ucs": ucs,
    "astar": astar
}
