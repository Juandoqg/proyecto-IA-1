from flask import Flask, jsonify, render_template
from flask_cors import CORS
import os

from graph import Node, Graph
from bfs import bfs_with_puzzles
from puzzle import create_puzzle

app = Flask(__name__, static_folder="static")
CORS(app)


def build_graph():
    """Construye el grafo del escape room desde cero."""
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

    return g, [A, H]


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/solve", methods=["GET"])
def solve():
    """
    Ejecuta BFS + A* completo y devuelve todos los frames + métricas finales.
    El frontend recibe esto una sola vez y anima los frames localmente.
    """
    g, starts = build_graph()
    frames, metrics = bfs_with_puzzles(g, starts, "M", create_puzzle)

    return jsonify({
        "frames":  frames,
        "metrics": metrics,
    })


if __name__ == "__main__":
    os.makedirs("static", exist_ok=True)
    print("=" * 50)
    print("  Escape Room Solver — Flask")
    print("  http://localhost:5000")
    print("=" * 50)
    app.run(debug=True, port=5000)
