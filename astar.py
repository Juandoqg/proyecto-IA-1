import heapq


def solve_puzzle(puzzle, frames, unlock_node):
    """
    Ejecuta el algoritmo A* sobre un subgrafo (puzzle).

     Parámetros:
    - puzzle: diccionario con la definición del subproblema:
        {
            "start": nodo inicial,
            "goal": nodo objetivo,
            "graph": grafo (adyacencias con costos),
            "heuristic": función heurística h(n)
        }

    - frames: lista donde se registran TODOS los estados del algoritmo
              (para animación en frontend)

    - unlock_node: nombre del nodo del grafo global que será desbloqueado
                   al resolver este puzzle

     Retorna:
    - (True/False) → si se resolvió el puzzle
    - costo total
    - métricas del A*
    """

    # -------------------------
    # Inicialización
    # -------------------------
    start    = puzzle["start"]
    goal     = puzzle["goal"]
    graph    = puzzle["graph"]
    heuristic = puzzle["heuristic"]

    # Cola de prioridad (min-heap) → ordenada por f(n) = g(n) + h(n)
    open_list = []
    heapq.heappush(open_list, (heuristic(start), start))

    # g(n): costo acumulado desde el inicio
    g_cost    = {start: 0}

    # Para reconstruir el camino final
    came_from = {start: None}

    # Conjunto de nodos ya expandidos
    visited   = set()

    # Métrica: nodos expandidos
    nodes_expanded = 0

    # -------------------------
    # Frame inicial del puzzle
    # -------------------------
    frames.append({
        "type": "puzzle_start",
        "unlock_node": unlock_node,

        # Logs para UI
        "log_bfs":   f"Nodo bloqueado '{unlock_node}' — iniciando A*...",
        "log_astar": f"A* iniciado | start='{start}'  goal='{goal}'",

        # Estados visuales de nodos
        "puzzle_node_states": _puzzle_states(visited, None, goal, start),

        # Información de A*
        "puzzle_gcost": dict(g_cost),
        "puzzle_nodes_expanded": 0,
        "puzzle_cost": "—",
        "puzzle_path": "—",
    })

    # -------------------------
    # Bucle principal de A*
    # -------------------------
    while open_list:
        # Extrae el nodo con menor f(n)
        f, current = heapq.heappop(open_list)

        # Evita reprocesar nodos
        if current in visited:
            continue

        visited.add(current)
        nodes_expanded += 1

        # -------------------------
        # Frame: expansión de nodo
        # -------------------------
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

        # -------------------------
        # Si llegó al objetivo
        # -------------------------
        if current == goal:
            path, node = [], current

            # Reconstrucción del camino usando came_from
            while node is not None:
                path.append(node)
                node = came_from[node]
            path.reverse()

            # -------------------------
            # Frame: solución encontrada
            # -------------------------
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

        # -------------------------
        # Expansión de vecinos
        # -------------------------
        for neighbor, cost in graph.get(current, []):

            # Nuevo costo acumulado
            new_cost = g_cost[current] + cost

            # Relajación (condición típica de A*)
            if neighbor not in g_cost or new_cost < g_cost[neighbor]:
                g_cost[neighbor]    = new_cost
                came_from[neighbor] = current

                # f(n) = g(n) + h(n)
                f_val = new_cost + heuristic(neighbor)

                heapq.heappush(open_list, (f_val, neighbor))

                # -------------------------
                # Frame: nodo encolado
                # -------------------------
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

    # -------------------------
    # Si no hay solución
    # -------------------------
    return False, float("inf"), {
        "nodes_expanded": nodes_expanded,
        "path": [],
        "cost": float("inf")
    }


def _puzzle_states(visited, current, goal, start):
    """
    Genera el estado visual de cada nodo del puzzle.

     Estados posibles:
    - start      → nodo inicial
    - expanding  → nodo actual (en expansión)
    - expanded   → nodo ya visitado
    - goal       → nodo objetivo alcanzado
    - available  → nodo aún no explorado

     Se usa para pintar el grafo en el frontend.
    """

    states = {}

    #  NOTA: actualmente está HARDCODEADO para nodos A-E
    # (esto se puede mejorar para hacerlo dinámico)
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