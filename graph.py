class Node:
    """
    Representa un nodo dentro del grafo del escape room.

    Un nodo modela un estado del juego. Puede estar:
    - libre (available)
    - bloqueado (locked)
    - asociado a un puzzle (subproblema A*)

    Atributos:
    - name: identificador único del nodo
    - locked: indica si el nodo está bloqueado
    - puzzle: estructura del subproblema asociado (si aplica)
    """

    def __init__(self, name, locked=False, puzzle=None):
        self.name = name          # Nombre único del nodo
        self.locked = locked      # Estado: bloqueado o no
        self.puzzle = puzzle      # Subproblema (para A*)

    def __repr__(self):
        """
        Representación en texto del nodo.
        Útil para debugging.
        """
        return f"Node({self.name}, locked={self.locked})"


class Graph:
    """
    Representa el grafo dirigido del escape room.

    Se implementa como una lista de adyacencia:
    {
        "A": [Node(B), Node(E)],
        "B": [Node(C)],
        ...
    }

    Nota: el grafo almacena referencias a objetos Node,
    pero indexa por nombre (string).
    """

    def __init__(self):
        # Diccionario de adyacencia
        # clave: nombre del nodo origen
        # valor: lista de nodos destino
        self.adj = {}

    def add_edge(self, u, v):
        """
        Agrega una arista dirigida u → v.

        Parámetros:
        - u: nodo origen (Node)
        - v: nodo destino (Node)
        """
        if u.name not in self.adj:
            self.adj[u.name] = []

        self.adj[u.name].append(v)

    def neighbors(self, node):
        """
        Retorna los vecinos (nodos alcanzables) desde un nodo dado.

        Parámetros:
        - node: instancia de Node

        Retorna:
        - lista de nodos vecinos
        """
        return self.adj.get(node.name, [])