import heapq

def solve_puzzle(puzzle):
    start = puzzle["start"]
    goal = puzzle["goal"]
    graph = puzzle["graph"]
    heuristic = puzzle["heuristic"]

    open_list = []
    heapq.heappush(open_list, (heuristic(start), start))

    g_cost = {start: 0}
    visited = set()
    nodes_expanded = 0
    came_from = {start: None}

    print(f"  [A*] Iniciando desde '{start}' hacia '{goal}'")

    while open_list:
        f, current = heapq.heappop(open_list)

        if current in visited:
            continue

        visited.add(current)
        nodes_expanded += 1
        print(f"  [A*] Expandiendo '{current}' | f={f} g={g_cost[current]} h={heuristic(current)}")

        if current == goal:
            # Reconstruir camino
            path = []
            node = current
            while node is not None:
                path.append(node)
                node = came_from[node]
            path.reverse()
            print(f"  [A*] Solucion encontrada: {' -> '.join(path)} | costo={g_cost[current]}")
            return True, g_cost[current], {
                "nodes_expanded": nodes_expanded,
                "path": path,
                "cost": g_cost[current]
            }

        for neighbor, cost in graph.get(current, []):
            new_cost = g_cost[current] + cost
            if neighbor not in g_cost or new_cost < g_cost[neighbor]:
                g_cost[neighbor] = new_cost
                came_from[neighbor] = current
                f_val = new_cost + heuristic(neighbor)
                heapq.heappush(open_list, (f_val, neighbor))
                print(f"  [A*]   -> '{neighbor}' g={new_cost} h={heuristic(neighbor)} f={f_val}")

    print("  [A*] No se encontro solucion.")
    return False, float("inf"), {"nodes_expanded": nodes_expanded, "path": [], "cost": float("inf")}
