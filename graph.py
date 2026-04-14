class Node:
    # esto representa una sola habitacion en el Escape Room
    def __init__(self, name, locked=False, puzzle=None):
        self.name = name          # nombre de la sala
        self.locked = locked      # si esta bloqueada o no
        self.puzzle = puzzle      # el puzzle que tiene adentro por si esta bloqueada

    def __repr__(self):
        # para verlo facil al imprimir
        return f"Node({self.name}, locked={self.locked})"

class Graph:
    # este es el mapa que guarda todas las conexiones
    def __init__(self):
        # aca guardamos que habitacion conecta con cual
        self.adj = {}

    def add_edge(self, u, v):
        # agregamos un camino desde la habitacion u a la v
        if u.name not in self.adj:
            self.adj[u.name] = []
        
        self.adj[u.name].append(v)

    def neighbors(self, node):
        # devuelve las habitaciones a las que podemos ir desde esta
        return self.adj.get(node.name, [])