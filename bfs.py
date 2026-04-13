from collections import deque
from astar import solve_puzzle


def bfs_with_puzzles(graph, starts, goal, puzzle_factory):
    """
    BFS desde múltiples nodos iniciales.
    Devuelve (frames, metrics) donde frames es la lista completa
    de pasos que el frontend animará.
    """
    if not isinstance(starts, list):
        starts = [starts]

    frames  = []
    metrics = {
        "nodes_expanded": 0,
        "max_depth":      0,
        "puzzles_solved": 0,
        "solution_path":  None,
        "solution_depth": None,
    }

    # Estado inicial de nodos del grafo global
    locked_nodes = {n.name for n in _all_nodes(graph) if n.locked}
    global_ns    = _build_node_states(graph, starts, locked_nodes, goal)

    queue   = deque()
    visited = set()

    for s in starts:
        queue.append((s, [s.name], 0))

    frames.append({
        "type": "bfs_init",
        "log_bfs": "BFS iniciado. Nodos raíz: " + ", ".join(s.name for s in starts),
        "global_node_states": dict(global_ns),
        "queue_size": len(queue),
        **_empty_puzzle_frame(),
        **_metrics_snapshot(metrics),
    })

    while queue:
        current_node, path, depth = queue.popleft()

        if current_node.name in visited:
            continue

        visited.add(current_node.name)
        metrics["nodes_expanded"] += 1
        metrics["max_depth"] = max(metrics["max_depth"], depth)

        if current_node.name not in [s.name for s in starts]:
            global_ns[current_node.name] = "expanded"

        frames.append({
            "type": "bfs_expand",
            "node": current_node.name,
            "depth": depth,
            "path": path,
            "log_bfs": f"Expandiendo '{current_node.name}'  prof={depth}  camino={' → '.join(path)}",
            "global_node_states": dict(global_ns),
            "queue_size": len(queue),
            **_empty_puzzle_frame(),
            **_metrics_snapshot(metrics),
        })

        if current_node.name == goal:
            metrics["solution_path"]  = path
            metrics["solution_depth"] = depth
            # Marcar camino solución
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

        for neighbor in graph.neighbors(current_node):
            if neighbor.name in visited:
                continue

            if neighbor.locked:
                # Pausar BFS y resolver puzzle con A*
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

                solved, cost, local_m = solve_puzzle(
                    neighbor.puzzle, frames, neighbor.name
                )

                if solved:
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

            queue.append((neighbor, path + [neighbor.name], depth + 1))
            frames.append({
                "type": "bfs_enqueue",
                "node": neighbor.name,
                "log_bfs": f"  → encolado '{neighbor.name}'",
                "global_node_states": dict(global_ns),
                "queue_size": len(queue),
                **_empty_puzzle_frame(),
                **_metrics_snapshot(metrics),
            })

    return frames, metrics


# ── Helpers ──────────────────────────────────────────────────────────────────

def _all_nodes(graph):
    seen, result = set(), []
    for name, neighbors in graph.adj.items():
        # We need Node objects; graph stores them as values
        for n in neighbors:
            if n.name not in seen:
                seen.add(n.name)
                result.append(n)
    return result


def _build_node_states(graph, starts, locked_nodes, goal):
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
    return {
        "puzzle_node_states":    {},
        "puzzle_gcost":          {},
        "puzzle_nodes_expanded": 0,
        "puzzle_cost":           "—",
        "puzzle_path":           "—",
    }


def _metrics_snapshot(m):
    return {
        "bfs_nodes_expanded": m["nodes_expanded"],
        "bfs_max_depth":      m["max_depth"],
        "bfs_puzzles_solved": m["puzzles_solved"],
    }
