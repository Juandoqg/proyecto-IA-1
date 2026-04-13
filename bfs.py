from collections import deque
import time
from astar import solve_puzzle


def bfs_with_puzzles(graph, starts, goal, metrics):
    """
    BFS desde uno o varios nodos iniciales.
    Cuando encuentra un nodo bloqueado, lanza A* para desbloquearlo.
    Una vez desbloqueado, el nodo queda libre para todos.
    """
    # Admite un solo nodo o lista de nodos como inicio
    if not isinstance(starts, list):
        starts = [starts]

    queue = deque()
    visited = set()

    for s in starts:
        queue.append((s, [s], 0))
        print(f"[BFS] Nodo inicial: {s.name}")

    start_time = time.time()
    puzzle_metrics = {}

    while queue:
        current, path, depth = queue.popleft()

        if current.name in visited:
            continue

        visited.add(current.name)
        metrics["nodes_expanded"] += 1
        metrics["max_depth"] = max(metrics.get("max_depth", 0), depth)

        print(f"[BFS] Expandiendo '{current.name}' | profundidad={depth} | camino={[n.name for n in path]}")

        if current.name == goal:
            metrics["execution_time"] = round(time.time() - start_time, 4)
            metrics["solution_path"] = [n.name for n in path]
            metrics["solution_depth"] = depth
            metrics["puzzle_metrics"] = puzzle_metrics
            print(f"\n[BFS] META ALCANZADA: {' -> '.join(n.name for n in path)}")
            return path

        for neighbor in graph.neighbors(current):
            if neighbor.name in visited:
                continue

            if neighbor.locked:
                print(f"\n[BFS] Nodo bloqueado encontrado: '{neighbor.name}'")
                print(f"[BFS] Iniciando busqueda informada (A*) para desbloquear '{neighbor.name}'...\n")

                solved, cost, local_m = solve_puzzle(neighbor.puzzle)

                if solved:
                    print(f"\n[BFS] Puzzle resuelto! Desbloqueando '{neighbor.name}'")
                    neighbor.locked = False
                    puzzle_metrics[neighbor.name] = local_m
                    metrics["puzzles_solved"] = metrics.get("puzzles_solved", 0) + 1
                else:
                    print(f"[BFS] No se pudo resolver el puzzle de '{neighbor.name}'. Nodo omitido.")
                    continue

            queue.append((neighbor, path + [neighbor], depth + 1))

    metrics["execution_time"] = round(time.time() - start_time, 4)
    print("[BFS] Cola vacia. No se encontro camino a la meta.")
    return None
