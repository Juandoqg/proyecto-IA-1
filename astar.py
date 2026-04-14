import heapq

def solve_puzzle(puzzle, frames, unlock_node):
    # aplicamos el algoritmo A* para resolver este minijuego y poder abrir la puerta
    
    start    = puzzle["start"]
    goal     = puzzle["goal"]
    graph    = puzzle["graph"]
    heuristic = puzzle["heuristic"]

    # aca guardamos los caminos ordenados para que sea inteligente y rapido
    open_list = []
    heapq.heappush(open_list, (heuristic(start), start))

    # registramos lo que llevamos gastado caminando
    g_cost    = {start: 0}

    # nos va dejar un rastro de poder volver hacia atras y recordar por donde fuimos
    came_from = {start: None}

    # las salas de este minijuego que ya hemos abierto
    visited   = set()
    nodes_expanded = 0
    nodes_created  = 1

    # creamos la primera escena de la animacion de la web
    frames.append({
        "type": "puzzle_start",
        "unlock_node": unlock_node,
        "log_bfs":   f"Intentando abrir la sala '{unlock_node}'...",
        "log_astar": f"Nodo creado (Inicio): {start}",
        "puzzle_node_states": _puzzle_states(graph, visited, None, goal, start),
        "puzzle_gcost": dict(g_cost),
        "puzzle_nodes_expanded": 0,
        "puzzle_nodes_created": 1,
        "puzzle_cost": "—",
        "puzzle_path": "—",
    })

    # sigue revisando mientras tengamos un lugar donde ir
    while open_list:
        # esto saca la opcion mas prometedora (que tenga menor costo y la de mejor corazonada)
        f, current = heapq.heappop(open_list)

        # si esto ya lo visitamos lo saltamos
        if current in visited:
            continue

        visited.add(current)
        nodes_expanded += 1

        # agregamos este pasito a nuestra animacion
        frames.append({
            "type": "puzzle_expand",
            "unlock_node": unlock_node,
            "current": current,
            "log_astar": f"Nodo expandido: {current}",
            "puzzle_node_states": _puzzle_states(graph, visited, current, goal, start),
            "puzzle_gcost": dict(g_cost),
            "puzzle_nodes_expanded": nodes_expanded,
            "puzzle_nodes_created": nodes_created,
            "puzzle_cost": "—",
            "puzzle_path": "—",
        })

        # ganamos el minijuego!
        if current == goal:
            path, node = [], current

            # vamos recorriendo hacia atras para trazar la ruta usada
            while node is not None:
                path.append(node)
                node = came_from[node]
            # y la damos vuelta de inicio al final que es como la queremos ver
            path.reverse()

            frames.append({
                "type": "puzzle_solved",
                "unlock_node": unlock_node,
                "cost": g_cost[current],
                "path": path,
                "log_bfs":   f"Pudimos abrir la sala '{unlock_node}'",
                "log_astar": f"Minijuego completado con costo total: {g_cost[current]}",
                "puzzle_node_states": _puzzle_states(graph, visited, current, goal, start),
                "puzzle_gcost": dict(g_cost),
                "puzzle_nodes_expanded": nodes_expanded,
                "puzzle_nodes_created": nodes_created,
                "puzzle_cost": g_cost[current],
                "puzzle_path": " -> ".join(path),
            })

            # devolvemos todo si ganamos
            return True, g_cost[current], {
                "nodes_expanded": nodes_expanded,
                "path": path,
                "cost": g_cost[current],
            }

        # miramos las habitaciones vecinitas de adentro del minijuego
        for neighbor, cost in graph.get(current, []):
            # esto revisa el costo para ir por alli
            new_cost = g_cost[current] + cost

            # si sale mas barato nos metemos y anotamos eso
            if neighbor not in g_cost or new_cost < g_cost[neighbor]:
                g_cost[neighbor]    = new_cost
                
                came_from[neighbor] = current

                # juntamos todos los calculos: cuanto va mas cuanto pienso que me falta (corazonada)
                f_val = new_cost + heuristic(neighbor)
                
                # lo agregamos a nuestra lista ordenada y lo mete por precio
                heapq.heappush(open_list, (f_val, neighbor))
                nodes_created += 1

                frames.append({
                    "type": "puzzle_enqueue",
                    "unlock_node": unlock_node,
                    "from_node": current,
                    "to_node":   neighbor,
                    "log_astar": f"Nodo creado: {neighbor}",
                    "puzzle_node_states": _puzzle_states(graph, visited, current, goal, start),
                    "puzzle_gcost": dict(g_cost),
                    "puzzle_nodes_expanded": nodes_expanded,
                    "puzzle_nodes_created": nodes_created,
                    "puzzle_cost": "—",
                    "puzzle_path": "—",
                })

    # si se daña y no pudimos resolverlo devolvemos algo super alto e invalido
    return False, float("inf"), {
        "nodes_expanded": nodes_expanded,
        "path": [],
        "cost": float("inf")
    }


def _puzzle_states(graph, visited, current, goal, start):
    # solo nos da colores para que el frente nos lo muestre bonito
    states = {}
    nodes = _extract_nodes(graph)

    for n in nodes:
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


def _extract_nodes(graph):
    # saca los puntitos (salas) pero para este mapa adentro de otro mapa 
    nodes = set()
    for n, neighbors in graph.items():
        nodes.add(n)
        for nb, _ in neighbors:
            nodes.add(nb)
    return nodes