from graph import Node, Graph
from bfs import bfs_with_puzzles
from puzzle import create_puzzle

# ---------- Nodos ----------
A = Node("A")
B = Node("B")
C = Node("C", locked=True,  puzzle=create_puzzle())
E = Node("E")
G = Node("G")
H = Node("H")
I = Node("I")
J = Node("J")
K = Node("K", locked=True,  puzzle=create_puzzle())
L = Node("L")
M = Node("M")  # META

# ---------- Grafo global ----------
g = Graph()
g.add_edge(A, B)
g.add_edge(A, E)
g.add_edge(B, C)
g.add_edge(E, G)
g.add_edge(E, C)
g.add_edge(H, G)
g.add_edge(H, J)
g.add_edge(G, K)
g.add_edge(J, K)
g.add_edge(C, I)
g.add_edge(G, I)
g.add_edge(I, L)
g.add_edge(K, L)
g.add_edge(K, M)
g.add_edge(L, M)

# ---------- Métricas ----------
metrics = {
    "nodes_expanded": 0,
    "max_depth": 0,
    "execution_time": 0,
    "puzzles_solved": 0,
}

# H entra como segunda raíz del BFS
starts = [A, H]

print("=" * 55)
print("  ESCAPE ROOM SOLVER")
print("  BFS global + A* para nodos bloqueados")
print(f"  Nodos bloqueados: C, K")
print(f"  Meta: M")
print("=" * 55 + "\n")

result = bfs_with_puzzles(g, starts, "M", metrics)

print("\n" + "=" * 55)
print("  RESULTADOS")
print("=" * 55)
if result:
    print(f"  Camino solución : {' -> '.join(n.name for n in result)}")
    print(f"  Profundidad     : {metrics['solution_depth']}")
else:
    print("  No se encontró camino a la meta.")

print(f"\n  --- Métricas globales ---")
print(f"  Nodos expandidos : {metrics['nodes_expanded']}")
print(f"  Profundidad max  : {metrics['max_depth']}")
print(f"  Puzzles resueltos: {metrics['puzzles_solved']}")
print(f"  Tiempo ejecución : {metrics['execution_time']}s")

if "puzzle_metrics" in metrics:
    print(f"\n  --- Métricas por puzzle ---")
    for node_name, pm in metrics["puzzle_metrics"].items():
        print(f"  Nodo {node_name}: expandidos={pm['nodes_expanded']} costo={pm['cost']} camino={' -> '.join(pm['path'])}")
print("=" * 55)
