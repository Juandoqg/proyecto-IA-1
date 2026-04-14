from collections import deque
from astar import solve_puzzle

def bfs_with_puzzles(graph, starts, goal, puzzle_factory):
    # funcion principal que busca la salida del escape room usando BFS
    # cuando se encuentra una puerta cerrada, usa el A*

    # esto es por si mandamos un solo inicio o la lista de inicios
    if not isinstance(starts, list):
        starts = [starts]

    # la lista donde guardamos todos los frames de video para la animacion de la web
    frames  = []

    # esto nos sirve para mostrar las estadisticas al final
    metrics = {
        "nodes_expanded": 0,
        "nodes_created":  len(starts),
        "max_depth":      0,
        "puzzles_solved": 0,
        "solution_path":  None,
        "solution_depth": None,
    }

    # vemos que habitaciones tienen candado
    locked_nodes = {n.name for n in _all_nodes(graph) if n.locked}

    # preparamos todo lo inicial para que en la web se vea de color gris
    global_ns = _build_node_states(graph, starts, locked_nodes, goal)

    # la cola para nuestro algoritmo BFS
    queue   = deque()
    visited = set()

    # agregamos las primeras salas a la cola
    for s in starts:
        queue.append((s, [s.name], 0))

    # guardamos el primer paso de nuestra animacion
    frames.append({
        "type": "bfs_init",
        "log_bfs": f"Nodos creados: {', '.join(s.name for s in starts)}",
        "global_node_states": dict(global_ns),
        "queue_size": len(queue),
        **_empty_puzzle_frame(),
        **_metrics_snapshot(metrics),
    })

    # seguimos sacando de la cola hasta que se acabe
    while queue:
        current_node, path, depth = queue.popleft()

        # si ya estuvimos en esta sala, la ignoramos
        if current_node.name in visited:
            continue

        visited.add(current_node.name)

        # contamos que vimos otro nodo
        metrics["nodes_expanded"] += 1
        metrics["max_depth"] = max(metrics["max_depth"], depth)

        # cambiamos el color a expandido
        if current_node.name not in [s.name for s in starts]:
            global_ns[current_node.name] = "expanded"

        # guardamos el frame
        frames.append({
            "type": "bfs_expand",
            "node": current_node.name,
            "depth": depth,
            "path": path,
            "log_bfs": f"Nodo expandido: {current_node.name}",
            "global_node_states": dict(global_ns),
            "queue_size": len(queue),
            **_empty_puzzle_frame(),
            **_metrics_snapshot(metrics),
        })

        # comprobamos si llegamos a la salida del juego
        if current_node.name == goal:
            metrics["solution_path"]  = path
            metrics["solution_depth"] = depth

            # coloreamos las salas de nuestro camino ganador
            for n in path:
                if global_ns.get(n) not in ("start", "goal"):
                    global_ns[n] = "inpath"

            global_ns[goal] = "goal"

            # frame final!!
            frames.append({
                "type": "bfs_goal",
                "path": path,
                "log_bfs": f"LLEGASTE AL FINAL: {' -> '.join(path)}",
                "global_node_states": dict(global_ns),
                "queue_size": 0,
                **_empty_puzzle_frame(),
                **_metrics_snapshot(metrics),
            })
            break

        # traemos las habitaciones de al lado (las vecinas)
        for neighbor in graph.neighbors(current_node):
            if neighbor.name in visited:
                continue

            # si la habitacion de al lado tiene candado
            if neighbor.locked:
                global_ns[neighbor.name] = "locked"

                frames.append({
                    "type": "bfs_locked",
                    "node": neighbor.name,
                    "log_bfs": f"¡Uy! sala '{neighbor.name}' cerrada, hay que resolver el puzzle",
                    "global_node_states": dict(global_ns),
                    "queue_size": len(queue),
                    **_empty_puzzle_frame(),
                    **_metrics_snapshot(metrics),
                })

                # llamamos al otro algoritmo y la intentamos resolver
                solved, cost, local_m = solve_puzzle(
                    neighbor.puzzle, frames, neighbor.name
                )

                if solved:
                    # como le ganamos al puzzle, le quitamos el candado
                    neighbor.locked = False
                    metrics["puzzles_solved"] += 1
                    global_ns[neighbor.name] = "unlocked"

                    frames.append({
                        "type": "bfs_unlocked",
                        "node": neighbor.name,
                        "log_bfs": f"Sala '{neighbor.name}' desbloqueada!",
                        "global_node_states": dict(global_ns),
                        "queue_size": len(queue) + 1,
                        **_empty_puzzle_frame(),
                        **_metrics_snapshot(metrics),
                    })
                else:
                    # si fallamos, no podemos avanzar a esa sala
                    frames.append({
                        "type": "bfs_puzzle_failed",
                        "node": neighbor.name,
                        "log_bfs": f"No abrimos sala '{neighbor.name}'",
                        "global_node_states": dict(global_ns),
                        "queue_size": len(queue),
                        **_empty_puzzle_frame(),
                        **_metrics_snapshot(metrics),
                    })
                    continue

            # agregamos la sala a la cola 
            queue.append((neighbor, path + [neighbor.name], depth + 1))
            metrics["nodes_created"] += 1

            frames.append({
                "type": "bfs_enqueue",
                "node": neighbor.name,
                "log_bfs": f"Nodo creado: {neighbor.name}",
                "global_node_states": dict(global_ns),
                "queue_size": len(queue),
                **_empty_puzzle_frame(),
                **_metrics_snapshot(metrics),
            })

    # pasamos los datos para mostrarlos en el frontend (navegador web)
    return frames, metrics


def _all_nodes(graph):
    # saca todos los nodos que hay metidos en nuestro grafo
    seen, result = set(), []
    for name, neighbors in graph.adj.items():
        for n in neighbors:
            if n.name not in seen:
                seen.add(n.name)
                result.append(n)
    return result


def _build_node_states(graph, starts, locked_nodes, goal):
    # funcion auxiliar para ponerle color gris al principio 
    all_names = set()
    for name, neighbors in graph.adj.items():
        all_names.add(name)
        for n in neighbors:
            all_names.add(n.name)

    states = {}
    start_names = {s.name for s in starts}

    for n in all_names:
        if n in start_names:
            states[n] = "start"
        elif n == goal:
            states[n] = "available"
        elif n in locked_nodes:
            states[n] = "locked"
        else:
            states[n] = "available"

    return states


def _empty_puzzle_frame():
    # como en este turno no hubo puzzle devolvemos datos vacios para no dañar el frontend
    return {
        "puzzle_node_states":    {},
        "puzzle_gcost":          {},
        "puzzle_nodes_expanded": 0,
        "puzzle_nodes_created":  0,
        "puzzle_cost":           "—",
        "puzzle_path":           "—",
    }


def _metrics_snapshot(m):
    # manda una fotito para el lado derecho de la pantalla
    return {
        "bfs_nodes_expanded": m["nodes_expanded"],
        "bfs_nodes_created":  m["nodes_created"],
        "bfs_max_depth":      m["max_depth"],
        "bfs_puzzles_solved": m["puzzles_solved"],
    }