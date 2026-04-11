class Node:
    def __init__(self, name, locked=False, puzzle=None):
        self.name = name
        self.locked = locked
        self.puzzle = puzzle  # Subgrafo si está bloqueado

class Graph:
    def __init__(self):
        self.adj = {}

    def add_edge(self, u, v):
        if u not in self.adj:
            self.adj[u] = []
        self.adj[u].append(v)

    def neighbors(self, node):
        return self.adj.get(node, [])