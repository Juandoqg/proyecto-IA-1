# Informe del Proyecto: Escape Room Solver

## 1. Introducción
El presente proyecto consiste en un simulador diseñado para resolver un "Escape Room" de manera completamente automática. Para modelar este sistema, las habitaciones del juego y sus pasillos fueron representadas mediante en la memoria mediante un modelo de Grafo.

## 2. Arquitectura del Sistema
El núcleo del proyecto radica en la implementación de una Arquitectura Híbrida, la cual combina dos algoritmos de búsqueda trabajando de forma complementaria:

* **Búsqueda en Anchura (BFS):** Funciona como el algoritmo de exploración principal. Avanza cuarto por cuarto de forma panorámica e iterativa buscando la ruta más corta hacia la salida general del juego.
* **Algoritmo A* (A-Estrella):** Funciona como el algoritmo experto en resolución de bloqueos. Cuando la exploración principal se topa con una puerta trancada, el sistema invoca al A* para que descifre un sub-acertijo local y abra el candado mediante el uso de heurísticas.

## 3. Flujo Lógico de Ejecución
La resolución del escenario transcurre mediante las siguientes fases metodológicas:

1. **Inicialización del entorno:** Se instancia el mapa principal con todas las habitaciones y se establecen las condiciones iniciales de barreras (nodos bloqueados).
2. **Exploración Global (BFS):** El sistema arranca en la habitación de entrada. El algoritmo identifica las habitaciones adyacentes y las va visitando de manera ordenada.
3. **Detección de Bloqueos:** Al intentar ingresar a una sala cuya validación de paso se encuentre cerrada, el avance global se suspende temporalmente.
4. **Resolución Local (A*):** El sistema transfiere el control temporal al algoritmo A*. Este evalúa el acertijo asociado al candado y utiliza una función de estimación (heurística) para evaluar la ruta de menor costo, descartando combinaciones poco óptimas.
5. **Liberación de Nodos:** Una vez solucionado el acertijo interno, el candado global se marca como resuelto y se permite el ingreso a la sala de forma definitiva.
6. **Continuación de la Ruta principal:** El BFS retoma su recorrido general exactamente donde pausó, explorando nuevas zonas seguras hasta alcanzar el estado objetivo Final.

## 4. Estructura de Componentes
El código se modularizó con las siguientes responsabilidades lógicas principales:

* **Módulos Base (`graph.py` y `puzzle.py`):** Encargados de definir los espacios lógicos mediante las clases `Node` y `Graph`. Constituyen la topología elemental e inyectan valores clave, como el diccionario de heurística.
* **Controlador Principal (`app.py`):** Coordina los flujos. A través de la función `setup_graph()` construye el diseño del mapa principal, y mediante el enrutador principal sirve de intermediario enviando el seguimiento de los algoritmos de Python hacia la pantalla web.
* **Motor BFS (`bfs.py`):** Centraliza la lógica de la búsqueda general en un sólo bloque (`bfs_with_puzzles`). Se apoya de una estructura "cola" tradicional en listas para garantizar que ninguna habitación conectada superficialmente quede sin recorrerse.
* **Motor A* (`astar.py`):** Aislado para manejar la búsqueda informada mediante la instrucción `solve_puzzle`. A diferencia de la cola tradicional, gestiona sus rutas matemáticas ordenándolas automáticamente con una estructura estricta de "cola de prioridad" (`heapq`), decidiendo internamente qué combinación de puerta resulta más barata de calcular.

## 5. Métricas Evaluadas
Para observar el esfuerzo de trabajo del sistema, el algoritmo emite dos métricas de rendimiento en tiempo real:
* **Generación de Nodos (Nodos Creados):** Ocurre cuando el algoritmo descubre un nodo vecino. Esto indica que un camino fue visibilizado y es almacenado en la cola para su evaluación a futuro.
* **Expansión de Nodos (Nodos Expandidos):** Representa el procesamiento final de un nodo. El algoritmo entra físicamente al nodo, revisa si es la meta, y prosigue a escanear todos los caminos que parten derivan desde él, dándolo por utilizado.
