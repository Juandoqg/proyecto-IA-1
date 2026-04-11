from graph import Node, Graph
from bfs import bfs_with_puzzles
from puzzle import create_puzzle

# Crear nodos
A = Node("A")
B = Node("B")
C = Node("C", locked=True, puzzle=create_puzzle())
E = Node("E")

# Grafo global
g = Graph()
g.add_edge(A, B)
g.add_edge(A, E)
g.add_edge(B, C)

metrics = {
    "nodes_expanded": 0,
    "execution_time": 0
}

result = bfs_with_puzzles(g, A, "C", metrics)

print("\nResultado:", [n.name for n in result])
print("Métricas:", metrics)