def create_puzzle():
    graph = {
        "A": [("B", 7)],
        "B": [("C", 3)],
        "C": [("D", 4), ("E", 8)],
        "D": [("E", 2)]
    }

    ##la heuristica que se definio es la distancia estimada al objetivo
    def heuristic(n):
        h = {
            "A": 10,
            "B": 8,
            "C": 5,
            "D": 2,
            "E": 0
        }
        return h[n]

    return {
        "start": "A",
        "goal": "E",
        "graph": graph,
        "heuristic": heuristic
    }