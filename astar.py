import heapq

def solve_puzzle(puzzle):
    start = puzzle["start"]
    goal = puzzle["goal"]
    graph = puzzle["graph"]
    heuristic = puzzle["heuristic"]

    open_list = []
    heapq.heappush(open_list, (0, start))

    g_cost = {start: 0}
    visited = set()

    nodes_expanded = 0

    while open_list:
        _, current = heapq.heappop(open_list)

        if current == goal:
            return True, g_cost[current], {"nodes_expanded": nodes_expanded}

        if current in visited:
            continue

        visited.add(current)
        nodes_expanded += 1

        for neighbor, cost in graph.get(current, []):
            new_cost = g_cost[current] + cost

            if neighbor not in g_cost or new_cost < g_cost[neighbor]:
                g_cost[neighbor] = new_cost
                f = new_cost + heuristic(neighbor)
                heapq.heappush(open_list, (f, neighbor))

    return False, float("inf"), {"nodes_expanded": nodes_expanded}