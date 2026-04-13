def create_puzzle():
    """
    Crea un subproblema (puzzle) que será resuelto con A*.

    Este puzzle representa un grafo independiente del grafo global.
    Se usa cuando el BFS encuentra un nodo bloqueado.

    Retorna un diccionario con:
    - start: nodo inicial
    - goal: nodo objetivo
    - graph: grafo del subproblema (adyacencias con costos)
    - heuristic: función heurística h(n)
    """

    # -------------------------
    # Definición del grafo
    # -------------------------
    # Representado como:
    # nodo -> lista de (vecino, costo)
    graph = {
        "A": [("B", 7)],
        "B": [("C", 3)],
        "C": [("D", 4), ("E", 8)],
        "D": [("E", 2)]
    }

    # -------------------------
    # Función heurística
    # -------------------------
    def heuristic(n):
        """
        Heurística h(n): estima el costo desde el nodo n hasta el objetivo.

        Valores definidos manualmente.
        Debe ser:
        - admisible (no sobreestimar)
        - consistente (idealmente)

        En este caso:
        A: 10
        B: 8
        C: 5
        D: 2
        E: 0 (objetivo)
        """
        h = {"A": 10, "B": 8, "C": 5, "D": 2, "E": 0}
        return h[n]

    # -------------------------
    # Retorno del puzzle
    # -------------------------
    return {
        "start": "A",
        "goal": "E",
        "graph": graph,
        "heuristic": heuristic
    }