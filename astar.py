import heapq


def solve_puzzle(puzzle, frames, unlock_node):
    """
    Ejecuta A* sobre el subgrafo del puzzle.
    Registra cada paso como un frame en lugar de imprimir.
    """
    start    = puzzle["start"]
    goal     = puzzle["goal"]
    graph    = puzzle["graph"]
    heuristic = puzzle["heuristic"]

    open_list = []
    heapq.heappush(open_list, (heuristic(start), start))

    g_cost    = {start: 0}
    came_from = {start: None}
    visited   = set()
    nodes_expanded = 0

    frames.append({
        "type": "puzzle_start",
        "unlock_node": unlock_node,
        "log_bfs":   f"Nodo bloqueado '{unlock_node}' — iniciando A*...",
        "log_astar": f"A* iniciado | start='{start}'  goal='{goal}'",
        "puzzle_node_states": _puzzle_states(visited, None, goal, start),
        "puzzle_gcost": dict(g_cost),
        "puzzle_nodes_expanded": 0,
        "puzzle_cost": "—",
        "puzzle_path": "—",
    })

    while open_list:
        f, current = heapq.heappop(open_list)
        if current in visited:
            continue

        visited.add(current)
        nodes_expanded += 1

        frames.append({
            "type": "puzzle_expand",
            "unlock_node": unlock_node,
            "current": current,
            "log_astar": f"Expande '{current}'  f={f}  g={g_cost[current]}  h={heuristic(current)}",
            "puzzle_node_states": _puzzle_states(visited, current, goal, start),
            "puzzle_gcost": dict(g_cost),
            "puzzle_nodes_expanded": nodes_expanded,
            "puzzle_cost": "—",
            "puzzle_path": "—",
        })

        if current == goal:
            path, node = [], current
            while node is not None:
                path.append(node)
                node = came_from[node]
            path.reverse()

            frames.append({
                "type": "puzzle_solved",
                "unlock_node": unlock_node,
                "cost": g_cost[current],
                "path": path,
                "log_bfs":   f"Puzzle resuelto. Desbloqueando '{unlock_node}'",
                "log_astar": f"Resuelto  costo={g_cost[current]}  camino={' → '.join(path)}",
                "puzzle_node_states": _puzzle_states(visited, current, goal, start),
                "puzzle_gcost": dict(g_cost),
                "puzzle_nodes_expanded": nodes_expanded,
                "puzzle_cost": g_cost[current],
                "puzzle_path": " → ".join(path),
            })
            return True, g_cost[current], {
                "nodes_expanded": nodes_expanded,
                "path": path,
                "cost": g_cost[current],
            }

        for neighbor, cost in graph.get(current, []):
            new_cost = g_cost[current] + cost
            if neighbor not in g_cost or new_cost < g_cost[neighbor]:
                g_cost[neighbor]    = new_cost
                came_from[neighbor] = current
                f_val = new_cost + heuristic(neighbor)
                heapq.heappush(open_list, (f_val, neighbor))
                frames.append({
                    "type": "puzzle_enqueue",
                    "unlock_node": unlock_node,
                    "from_node": current,
                    "to_node":   neighbor,
                    "log_astar": f"  {current}→{neighbor}  g={new_cost}  f={f_val}",
                    "puzzle_node_states": _puzzle_states(visited, current, goal, start),
                    "puzzle_gcost": dict(g_cost),
                    "puzzle_nodes_expanded": nodes_expanded,
                    "puzzle_cost": "—",
                    "puzzle_path": "—",
                })

    return False, float("inf"), {"nodes_expanded": nodes_expanded, "path": [], "cost": float("inf")}


def _puzzle_states(visited, current, goal, start):
    states = {}
    for n in ["A", "B", "C", "D", "E"]:
        if n == goal and n in visited:
            states[n] = "goal"
        elif n in visited:
            states[n] = "expanded"
        elif n == current:
            states[n] = "expanding"
        elif n == start:
            states[n] = "start"
        else:
            states[n] = "available"
    return states
