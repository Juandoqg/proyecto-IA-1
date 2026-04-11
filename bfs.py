from collections import deque
import time

def bfs_with_puzzles(graph, start, goal, metrics):
    queue = deque([(start, [start])])
    visited = set()

    start_time = time.time()

    while queue:
        current, path = queue.popleft()

        if current.name in visited:
            continue

        visited.add(current.name)
        metrics["nodes_expanded"] += 1

        print(f"Expanding node {current.name}")

        if current.name == goal:
            metrics["execution_time"] = time.time() - start_time
            return path

        for neighbor in graph.neighbors(current):
            if neighbor.locked:
                print(f"Encountered locked node {neighbor.name}")
                
                # Resolver puzzle con A*
                from astar import solve_puzzle
                solved, cost, local_metrics = solve_puzzle(neighbor.puzzle)

                if solved:
                    print(f"Puzzle solved! Unlocking {neighbor.name}")
                    neighbor.locked = False
                else:
                    continue

            queue.append((neighbor, path + [neighbor]))

    return None