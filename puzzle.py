def create_puzzle():
    # esto crea el minijuego que hay dentro de una habitacion bloqueada
    
    # asi se ve el mapa del puzzle
    graph = {
        "A": [("B", 7)],
        "B": [("C", 3)],
        "C": [("D", 4), ("E", 8)],
        "D": [("E", 2)]
    }

    def heuristic(n):
        # valores inventados que nos ayudan a saber si estamos cerca del final
        h = {"A": 10, "B": 8, "C": 5, "D": 2, "E": 0}
        return h[n]

    # devolvemos todo lo necesario para poder jugar
    return {
        "start": "A",
        "goal": "E",
        "graph": graph,
        "heuristic": heuristic
    }