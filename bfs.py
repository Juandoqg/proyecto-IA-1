from collections import deque
from astar import solve_puzzle


def bfs_with_puzzles(graph, starts, goal, puzzle_factory):
    """
    Ejecuta BFS sobre el grafo global del escape room, integrando resolución
    de nodos bloqueados mediante A*.

    Parámetros:
    - graph: instancia del grafo global
    - starts: nodo o lista de nodos iniciales
    - goal: nombre del nodo objetivo
    - puzzle_factory: (no se usa directamente aquí, pero permite extender la creación de puzzles)

    Retorna:
    - frames: lista de estados (pasos) para animación en frontend
    - metrics: métricas globales del algoritmo
    """

    # Asegura que starts sea lista (permite múltiples raíces)
    if not isinstance(starts, list):
        starts = [starts]

    # Lista de frames para animación
    frames  = []

    # Métricas globales del BFS
    metrics = {
        "nodes_expanded": 0,
        "max_depth":      0,
        "puzzles_solved": 0,
        "solution_path":  None,
        "solution_depth": None,
    }

    # -------------------------
    # Estado inicial del grafo
    # -------------------------

    # Identifica nodos bloqueados inicialmente
    locked_nodes = {n.name for n in _all_nodes(graph) if n.locked}

    # Construye estados visuales iniciales
    global_ns = _build_node_states(graph, starts, locked_nodes, goal)

    # Cola BFS: (nodo, camino, profundidad)
    queue   = deque()

    # Conjunto de nodos visitados
    visited = set()

    # Inicializa la cola con los nodos raíz
    for s in starts:
        queue.append((s, [s.name], 0))

    queue_nodes = [n[0].name for n in queue]


    # Frame inicial
    frames.append({
        "type": "bfs_init",
        "log_bfs": "BFS iniciado. Nodos raíz: " + ", ".join(s.name for s in starts),
        "global_node_states": dict(global_ns),
        "queue_size": len(queue),
        "queue_nodes": queue_nodes,

        # Información del puzzle vacía (no se ha iniciado A*)
        **_empty_puzzle_frame(),

        # Snapshot de métricas
        **_metrics_snapshot(metrics),
    })

    # -------------------------
    # Bucle principal BFS
    # -------------------------
    while queue:
        current_node, path, depth = queue.popleft()

        # Evita reprocesar nodos
        if current_node.name in visited:
            continue

        visited.add(current_node.name)

        # Actualiza métricas
        metrics["nodes_expanded"] += 1
        metrics["max_depth"] = max(metrics["max_depth"], depth)

        # Marca nodo como expandido (excepto raíces)
        if current_node.name not in [s.name for s in starts]:
            global_ns[current_node.name] = "expanded"

        
        queue_nodes = [n[0].name for n in queue]

        # Frame de expansión
        frames.append({
            "type": "bfs_expand",
            "node": current_node.name,
            "depth": depth,
            "path": path,
            "log_bfs": f"Expandiendo '{current_node.name}'  prof={depth}  camino={' → '.join(path)}",
            "global_node_states": dict(global_ns),
            "queue_size": len(queue),
            "queue_nodes": queue_nodes,
            **_empty_puzzle_frame(),
            **_metrics_snapshot(metrics),
        })

        # -------------------------
        # Verificación de meta
        # -------------------------
        if current_node.name == goal:
            metrics["solution_path"]  = path
            metrics["solution_depth"] = depth

            # Marca el camino solución
            for n in path:
                if global_ns.get(n) not in ("start", "goal"):
                    global_ns[n] = "inpath"

            global_ns[goal] = "goal"

            frames.append({
                "type": "bfs_goal",
                "path": path,
                "log_bfs": f"META ALCANZADA: {' → '.join(path)}",
                "global_node_states": dict(global_ns),
                "queue_size": 0,
                **_empty_puzzle_frame(),
                **_metrics_snapshot(metrics),
            })
            break

        # -------------------------
        # Expansión de vecinos
        # -------------------------
        for neighbor in graph.neighbors(current_node):

            # Evita nodos ya visitados
            if neighbor.name in visited:
                continue

            # -------------------------
            # Manejo de nodo bloqueado
            # -------------------------
            if neighbor.locked:
                # Marca visualmente como bloqueado
                global_ns[neighbor.name] = "locked"

                frames.append({
                    "type": "bfs_locked",
                    "node": neighbor.name,
                    "log_bfs": f"Nodo bloqueado encontrado: '{neighbor.name}'",
                    "global_node_states": dict(global_ns),
                    "queue_size": len(queue),
                    **_empty_puzzle_frame(),
                    **_metrics_snapshot(metrics),
                })

                # Ejecuta A* (subproblema)
                solved, cost, local_m = solve_puzzle(
                    neighbor.puzzle, frames, neighbor.name
                )

                if solved:
                    # Desbloquea el nodo global
                    neighbor.locked = False
                    metrics["puzzles_solved"] += 1
                    global_ns[neighbor.name] = "unlocked"

                    frames.append({
                        "type": "bfs_unlocked",
                        "node": neighbor.name,
                        "log_bfs": f"'{neighbor.name}' desbloqueado. BFS continúa.",
                        "global_node_states": dict(global_ns),
                        "queue_size": len(queue) + 1,
                        **_empty_puzzle_frame(),
                        **_metrics_snapshot(metrics),
                    })
                else:
                    # Si el puzzle falla, se ignora ese nodo
                    frames.append({
                        "type": "bfs_puzzle_failed",
                        "node": neighbor.name,
                        "log_bfs": f"No se pudo resolver el puzzle de '{neighbor.name}'. Nodo omitido.",
                        "global_node_states": dict(global_ns),
                        "queue_size": len(queue),
                        **_empty_puzzle_frame(),
                        **_metrics_snapshot(metrics),
                    })
                    continue

            # Encola el vecino (ya desbloqueado o nunca bloqueado)
            queue.append((neighbor, path + [neighbor.name], depth + 1))

            queue_nodes = [n[0].name for n in queue]

            frames.append({
                "type": "bfs_enqueue",
                "node": neighbor.name,
                "log_bfs": f"  → encolado '{neighbor.name}'",
                "global_node_states": dict(global_ns),
                "queue_size": len(queue),
                "queue_nodes": queue_nodes,


                **_empty_puzzle_frame(),
                **_metrics_snapshot(metrics),
            })

    return frames, metrics


# -------------------------
# Helpers
# -------------------------

def _all_nodes(graph):
    """
    Extrae todos los nodos del grafo recorriendo la lista de adyacencia.

    Nota: El grafo no almacena explícitamente todos los nodos,
    por lo que se reconstruyen a partir de las aristas.
    """
    seen, result = set(), []

    for name, neighbors in graph.adj.items():
        for n in neighbors:
            if n.name not in seen:
                seen.add(n.name)
                result.append(n)

    return result


def _build_node_states(graph, starts, locked_nodes, goal):
    """
    Construye el estado visual inicial de todos los nodos del grafo global.

    Estados posibles:
    - start
    - available
    - locked
    - goal (se marca al final)
    """
    all_names = set()

    # Recolecta todos los nombres de nodos
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
    """
    Retorna una estructura vacía del estado del puzzle.
    Se usa cuando el BFS está activo y no hay ejecución de A*.
    """
    return {
        "puzzle_node_states":    {},
        "puzzle_gcost":          {},
        "puzzle_hcost":          {},
        "puzzle_fcost":          {},
        "puzzle_nodes_expanded": 0,
        "puzzle_cost":           "—",
        "puzzle_path":           "—",
    }


def _metrics_snapshot(m):
    """
    Genera un snapshot de métricas del BFS en un momento dado.
    Se incluye en cada frame para facilitar visualización en frontend.
    """
    return {
        "bfs_nodes_expanded": m["nodes_expanded"],
        "bfs_max_depth":      m["max_depth"],
        "bfs_puzzles_solved": m["puzzles_solved"],
    }