# Escape Room Solver (BFS + A*)

## Descripción

Este proyecto implementa un sistema para resolver un escape room utilizando algoritmos de búsqueda en inteligencia artificial.

El entorno del juego se modela como un grafo dirigido, donde:

- Cada nodo representa un estado del juego
- Cada arista representa una acción posible
- Algunos nodos están bloqueados y requieren resolver un acertijo

El sistema utiliza una arquitectura híbrida:

- Búsqueda no informada (BFS) para recorrer el grafo principal
- Búsqueda informada (A*) para resolver los acertijos

---

## Conceptos básicos

### Nodo

Un nodo representa un estado dentro del juego.

Ejemplo:
A es el estado inicial  
M es el estado objetivo (salida del escape room)

---

### Nodo vecino

Un nodo vecino es un nodo al que se puede acceder directamente desde otro nodo mediante una arista.

Ejemplo:
Si existe una conexión A → B, entonces B es vecino de A.

---

### Grafo

Un grafo es una estructura compuesta por nodos y conexiones entre ellos.

En este proyecto, el grafo es dirigido, lo que significa que las conexiones tienen una dirección específica.

---

### Nodo bloqueado

Un nodo bloqueado es un estado al que no se puede acceder directamente.

Para poder acceder a este nodo, se debe resolver un subproblema (puzzle).

---

## Arquitectura del sistema

El sistema está compuesto por los siguientes módulos:

- app.py: servidor Flask y punto de entrada
- bfs.py: implementación de la búsqueda en amplitud (BFS)
- astar.py: implementación del algoritmo A*
- graph.py: definición de nodos y grafo
- puzzle.py: definición de los subproblemas
- templates/: interfaz HTML
- static/: archivos CSS y JavaScript

---

## Flujo de ejecución

1. El usuario accede a la aplicación en el navegador
2. Flask renderiza la interfaz gráfica
3. El frontend realiza una petición al endpoint /solve
4. El backend construye el grafo del problema
5. Se ejecuta BFS para recorrer el grafo
6. Cuando BFS encuentra un nodo bloqueado:
   - Se detiene temporalmente
   - Ejecuta A* sobre el puzzle asociado
7. Una vez resuelto el puzzle:
   - El nodo se desbloquea
   - BFS continúa su ejecución
8. El proceso continúa hasta alcanzar la meta
9. El sistema devuelve:
   - Lista de pasos (frames)
   - Métricas de ejecución

---

## Algoritmos utilizados

### BFS (Breadth-First Search)

Se utiliza para recorrer el grafo principal.

Características:
- Explora por niveles
- Garantiza encontrar la solución con menor profundidad
- No utiliza heurística

---

### A* (A estrella)

Se utiliza para resolver los puzzles.

Características:
- Usa una función heurística
- Encuentra el camino de menor costo
- Es más eficiente que BFS en subproblemas

---

## Estructura del grafo global

El sistema define un grafo con los siguientes nodos:

A, B, C, E, G, H, I, J, K, L, M

Nodos bloqueados:
- C
- K

Nodo objetivo:
- M

---

## Estructura del puzzle

Cada nodo bloqueado tiene un subgrafo independiente:

A → B (7)  
B → C (3)  
C → D (4), E (8)  
D → E (2)  

Nodo inicial: A  
Nodo objetivo: E  

---

## Heurística

El algoritmo A* utiliza la siguiente heurística:

A: 10  
B: 8  
C: 5  
D: 2  
E: 0  

Esta función estima el costo restante hasta el objetivo.

---

## Visualización

El sistema genera una lista de "frames" que representan cada paso del algoritmo.

Cada frame contiene:

- Estado de los nodos del grafo global
- Estado del puzzle
- Mensajes de ejecución
- Métricas parciales

El frontend utiliza estos frames para animar el proceso.

---

## Métricas

El sistema registra métricas tanto globales como locales.

### Global (BFS)
- Nodos expandidos
- Profundidad máxima
- Número de puzzles resueltos
- Camino solución
- Profundidad de la solución

### Local (A*)
- Nodos expandidos
- Costo del camino
- Camino solución

---

## Ejecución del proyecto

1. Crear entorno virtual:
python -m venv venv

2. Activar entorno ( Windows ):
venv\Scripts\activate
3. Instalar dependencias:
pip install -r requirements.txt
4. Ejecutar el servidor:
python app.py


---

## Posibles mejoras

- Soporte para múltiples tipos de puzzles
- Heurísticas dinámicas
- Persistencia del estado
- Visualización interactiva del grafo
- Edición de grafos desde la interfaz

---

## Autor

Proyecto académico de inteligencia artificial enfocado en la integración de algoritmos de búsqueda.