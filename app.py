from flask import Flask, jsonify, render_template
from flask_cors import CORS
import os
from graph import Node, Graph
from bfs import bfs_with_puzzles
from puzzle import create_puzzle

# creamos la app web
app = Flask(__name__, static_folder="static")
CORS(app)

def build_graph():
    # esta funcion arma el mapa del juego
    
    A = Node("A")
    B = Node("B")

    # esta habitacion tiene candado, hay que resolver el puzzle
    C = Node("C", locked=True, puzzle=create_puzzle())

    E = Node("E")
    G = Node("G")
    H = Node("H")
    I = Node("I")
    J = Node("J")

    # otra habitacion con puzzle
    K = Node("K", locked=True, puzzle=create_puzzle())

    L = Node("L")
    M = Node("M")  # la meta

    # creamos el grafo que conecta todo
    g = Graph()

    # unimos las habitaciones
    g.add_edge(A, B)
    g.add_edge(A, E)
    g.add_edge(A, H)
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

    # devolvemos el mapa y desde donde empezamos 
    return g, [A]

# nos lleva a la pagina principal
@app.route("/")
def index():
    return render_template("index.html")

# funcion principal para resolver
@app.route("/solve", methods=["GET"])
def solve():
    # armamos el mapa
    g, starts = build_graph()

    # le decimos que lo resuelva
    frames, metrics = bfs_with_puzzles(g, starts, "M", create_puzzle)

    # mandamos los datos a la pagina para verlos
    return jsonify({
        "frames":  frames,
        "metrics": metrics,
    })

# prendemos el servidor
if __name__ == "__main__":
    os.makedirs("static", exist_ok=True)
    print("Iniciando Escape Room en http://localhost:5000")
    app.run(debug=True, port=5000)