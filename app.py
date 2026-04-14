from flask import Flask, jsonify, render_template
from flask_cors import CORS
import os
import time
from graph import Node, Graph
from bfs import bfs_with_puzzles
from puzzle import create_puzzle


app = Flask(__name__, static_folder="static")

CORS(app)


def build_graph():
    """
    Construye el grafo principal del escape room.

    Cada nodo representa un estado del juego.
    Algunos nodos están bloqueados y contienen un puzzle (A*).

    Retorna:
    - grafo (Graph)
    - lista de nodos iniciales (starts)
    """

    # -------------------------
    # Creación de nodos
    # -------------------------
    A = Node("A")
    B = Node("B")

    # Nodo bloqueado con subproblema A*
    C = Node("C", locked=True, puzzle=create_puzzle())

    E = Node("E")
    G = Node("G")
    H = Node("H")
    I = Node("I")
    J = Node("J")

    # Otro nodo bloqueado
    K = Node("K", locked=True, puzzle=create_puzzle())

    L = Node("L")
    M = Node("M")  # Nodo objetivo (meta)

    # -------------------------
    # Construcción del grafo
    # -------------------------
    g = Graph()

    # Definición de transiciones (grafo dirigido)
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

    # BFS comienza desde dos nodos iniciales
    return g, [A, H]


# -------------------------
# Ruta principal (frontend)
# -------------------------
@app.route("/")
def index():
    """
    Renderiza la interfaz gráfica (HTML).
    """
    return render_template("index.html")


# -------------------------
# Endpoint principal del sistema
# -------------------------
@app.route("/solve", methods=["GET"])
def solve():
    """
    Ejecuta el algoritmo completo del escape room:

    1. Construye el grafo
    2. Ejecuta BFS
    3. Resuelve puzzles con A* cuando es necesario
    4. Genera frames para animación
    5. Retorna resultados al frontend

    Retorna:
    - frames: lista de estados paso a paso
    - metrics: métricas globales
    """
    # iniciar medición de tiempo
    start_time = time.time()
    
    # Construcción del problema
    g, starts = build_graph()

    # Ejecución del algoritmo híbrido BFS + A*
    frames, metrics = bfs_with_puzzles(g, starts, "M", create_puzzle)

    # calcular tiempo total
    execution_time = time.time() - start_time

    # agregar 
    metrics["execution_time"] = round(execution_time, 4)

    # Respuesta en formato JSON
    return jsonify({
        "frames":  frames,
        "metrics": metrics,
    })


# -------------------------
# Ejecución del servidor
# -------------------------
if __name__ == "__main__":
    os.makedirs("static", exist_ok=True)

    print("=" * 50)
    print("  Escape Room Solver — Flask")
    print("  http://localhost:5000")
    print("=" * 50)

    # Ejecuta servidor en modo debug
    app.run(debug=True, port=5000)