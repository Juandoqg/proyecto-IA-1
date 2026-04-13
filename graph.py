class Node:
    def __init__(self, name, locked=False, puzzle=None):
        self.name = name
        self.locked = locked
        self.puzzle = puzzle

    def __repr__(self):
        return f"Node({self.name}, locked={self.locked})"


class Graph:
    def __init__(self):
        self.adj = {}

    def add_edge(self, u, v):
        if u.name not in self.adj:
            self.adj[u.name] = []
        self.adj[u.name].append(v)

    def neighbors(self, node):
        return self.adj.get(node.name, [])
