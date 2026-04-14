    const GLOBAL_EDGES = [
      ["A", "B"], ["A", "E"], ["B", "C"], ["E", "G"], ["E", "C"],
      ["H", "G"], ["H", "J"], ["G", "K"], ["J", "K"],
      ["C", "I"], ["G", "I"], ["I", "L"], ["K", "L"], ["K", "M"], ["L", "M"]
    ];
    const NODE_POS = {
      A: { x: 75, y: 150 }, B: { x: 175, y: 75 }, C: { x: 295, y: 75 },
      E: { x: 175, y: 225 }, G: { x: 340, y: 190 }, H: { x: 555, y: 150 },
      I: { x: 390, y: 275 }, J: { x: 490, y: 230 }, K: { x: 475, y: 130 },
      L: { x: 555, y: 265 }, M: { x: 625, y: 190 }
    };
    const PUZZLE_POS = { A: { x: 28, y: 85 }, B: { x: 95, y: 45 }, C: { x: 165, y: 85 }, D: { x: 165, y: 135 }, E: { x: 255, y: 85 } };
    const PUZZLE_EDGES = [["A", "B", 7], ["B", "C", 3], ["C", "D", 4], ["C", "E", 8], ["D", "E", 2]];
    const LOCKED_NODES = new Set(["C", "K"]);
    const STARTS = ["A", "H"];

    const NODE_COLORS = {
      start: "#4ade80", available: "#60a5fa", locked: "#6b7280",
      expanded: "#a78bfa", expanding: "#fbbf24", unlocked: "#00d4aa",
      goal: "#f87171", inpath: "#f87171"
    };
    const NODE_TEXT = {
      start: "#052e16", available: "#1e3a5f", locked: "#1f2937",
      expanded: "#2e1065", expanding: "#451a03", unlocked: "#022c22",
      goal: "#450a0a", inpath: "#450a0a"
    };
    const STATUS_LABELS = {
      start: "inicial", available: "disponible", locked: "bloqueado",
      expanded: "expandido", expanding: "expandiendo", unlocked: "desbloqueado",
      goal: "meta", inpath: "en camino"
    };

    // ── Estado de la app ───────────────────────────────────────────────────────
    let ALL_FRAMES = [];
    let FINAL_METRICS = {};
    let cursor = -1;
    let autoTimer = null;
    const AUTO_DELAY = 550;

    // ── Fetch desde Flask ──────────────────────────────────────────────────────
    // GET /solve  →  { frames: [...], metrics: {...} }
    // Flask ejecuta BFS + A* completo en Python y devuelve el JSON.
    // El HTML solo anima los frames, no ejecuta ningún algoritmo.
    fetch("/solve")
      .then(r => r.json())
      .then(data => {
        ALL_FRAMES = data.frames;
        FINAL_METRICS = data.metrics;    // métricas finales calculadas por Python

        document.getElementById("s-time").textContent = data.metrics.execution_time ?? 0;
        document.getElementById("loading").style.display = "none";
        ["btn-step", "btn-auto", "btn-reset", "btn-back"].forEach(id =>
          document.getElementById(id).disabled = false
        );
        showFrame(0);
      })
      .catch(() => {
        document.getElementById("loading").innerHTML =
          '<span style="color:var(--red)">Error conectando con Flask. ¿Está corriendo app.py?</span>';
      });

    // ── Controles ──────────────────────────────────────────────────────────────
    function stepForward() {
      if (cursor < ALL_FRAMES.length - 1) showFrame(cursor + 1);
    }
    function stepBack() {
      if (cursor > 0) showFrame(cursor - 1);
    }
    function resetView() {
      if (autoTimer) { clearInterval(autoTimer); autoTimer = null; document.getElementById("btn-auto").innerHTML = "&#x25B6; Auto"; }
      // Rebuild log from scratch at frame 0
      document.getElementById("log-bfs").innerHTML = "";
      document.getElementById("log-astar").innerHTML = "";
      showFrame(0);
    }
    function toggleAuto() {
      if (autoTimer) {
        clearInterval(autoTimer); autoTimer = null;
        document.getElementById("btn-auto").innerHTML = "&#x25B6; Auto";
      } else {
        autoTimer = setInterval(() => {
          if (cursor >= ALL_FRAMES.length - 1) {
            clearInterval(autoTimer); autoTimer = null;
            document.getElementById("btn-auto").innerHTML = "&#x25B6; Auto";
            return;
          }
          stepForward();
        }, AUTO_DELAY);
        document.getElementById("btn-auto").innerHTML = "&#x23F8; Parar";
      }
    }

    // ── Renderizar un frame ────────────────────────────────────────────────────
    // Esta es la función central: toma un frame del array (producido por Python)
    // y actualiza todos los elementos visuales del HTML.
    function showFrame(idx) {
      cursor = idx;
      const f = ALL_FRAMES[idx];

      document.getElementById("frame-counter").textContent =
        `frame ${idx + 1} / ${ALL_FRAMES.length}  [${f.type}]`;

      // 1. Logs — solo agregamos si hay mensaje nuevo (no duplicamos al avanzar)
      if (f.log_bfs) appendLog("log-bfs", f.log_bfs, logClass(f.type, "bfs"));
      if (f.log_astar) appendLog("log-astar", f.log_astar, logClass(f.type, "astar"));

      // 2. Grafo global
      const currentExpanding = f.type === "bfs_expand" ? f.node : null;
      drawGlobalGraph(f.global_node_states || {}, currentExpanding, f.path || null);

      // 3. Grafo puzzle (solo visible cuando hay puzzle activo)
      const puzzleActive = f.type.startsWith("puzzle_");
      drawPuzzleGraph(
        puzzleActive ? (f.puzzle_node_states || {}) : {},
        puzzleActive ? (f.puzzle_gcost || {}) : {}
      );

      // 4. Estadísticas globales
      document.getElementById("s-exp").textContent = f.bfs_nodes_expanded ?? 0;
      document.getElementById("s-depth").textContent = f.bfs_max_depth ?? 0;
      document.getElementById("s-puzzles").textContent = f.bfs_puzzles_solved ?? 0;
      document.getElementById("s-queue").textContent = f.queue_size ?? 0;
      document.getElementById("queue-list").textContent = (f.queue_nodes && f.queue_nodes.length)
        ? f.queue_nodes.join(" → ")
        : "—";

      // 5. Estadísticas puzzle
      document.getElementById("p-exp").textContent = f.puzzle_nodes_expanded ?? 0;
      document.getElementById("p-cost").textContent = f.puzzle_cost ?? "—";
      document.getElementById("p-path").textContent = f.puzzle_path ?? "—";
      // g(n), h(n), f(n) del nodo actual del puzzle
      if (f.current) {
        document.getElementById("p-g").textContent =
          f.puzzle_gcost?.[f.current] ?? "—";

        document.getElementById("p-h").textContent =
          f.puzzle_hcost?.[f.current] ?? "—";

        document.getElementById("p-f").textContent =
          f.puzzle_fcost?.[f.current] ?? "—";
      } else {
        document.getElementById("p-g").textContent = "—";
        document.getElementById("p-h").textContent = "—";
        document.getElementById("p-f").textContent = "—";
        }

      // 6. Camino solución
      if (f.type === "bfs_goal") {
        document.getElementById("solution-path").textContent = f.path.join(" → ");
        document.getElementById("bfs-status").textContent = "meta alcanzada ✓";
        document.getElementById("bfs-status").style.color = "var(--green)";
      } else if (f.type.startsWith("puzzle_")) {
        document.getElementById("bfs-status").textContent =
          `resolviendo puzzle → ${f.unlock_node}`;
        document.getElementById("bfs-status").style.color = "var(--amber)";
      } else {
        document.getElementById("bfs-status").style.color = "var(--text3)";
        if (f.type === "bfs_init") document.getElementById("bfs-status").textContent = "ejecutando BFS";
      }

      // 7. Lista de nodos
      renderNodeList(f.global_node_states || {});
    }

    function logClass(frameType, side) {
      if (side === "bfs") {
        if (frameType === "bfs_goal" || frameType === "bfs_unlocked" || frameType === "puzzle_solved") return "ok";
        if (frameType === "bfs_locked") return "warn";
        if (frameType === "bfs_expand" || frameType === "bfs_init") return "info";
        return "dim";
      } else {
        if (frameType === "puzzle_solved") return "ok";
        if (frameType === "puzzle_expand") return "info";
        return "dim";
      }
    }

    // ── Dibujo SVG — Grafo global ──────────────────────────────────────────────
    const NS = "http://www.w3.org/2000/svg";

    function makeArrow(id) {
      const d = document.createElementNS(NS, "defs");
      d.innerHTML = `<marker id="${id}" viewBox="0 0 10 10" refX="9" refY="5"
    markerWidth="6" markerHeight="6" orient="auto-start-reverse">
    <path d="M1 1L9 5L1 9" fill="none" stroke="#3a3d50"
      stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></marker>`;
      return d;
    }

    function drawGlobalGraph(nodeStates, expanding, solutionPath) {
      const svg = document.getElementById("global-graph");
      svg.innerHTML = "";
      svg.appendChild(makeArrow("ag"));

      for (const [a, b] of GLOBAL_EDGES) {
        const pa = NODE_POS[a], pb = NODE_POS[b];
        const dx = pb.x - pa.x, dy = pb.y - pa.y, len = Math.sqrt(dx * dx + dy * dy);
        const r = 16;
        const x1 = pa.x + dx / len * r, y1 = pa.y + dy / len * r;
        const x2 = pb.x - dx / len * (r + 4), y2 = pb.y - dy / len * (r + 4);

        const onPath = solutionPath &&
          solutionPath.indexOf(a) >= 0 &&
          solutionPath.indexOf(b) === solutionPath.indexOf(a) + 1;

        const line = document.createElementNS(NS, "line");
        line.setAttribute("x1", x1); line.setAttribute("y1", y1);
        line.setAttribute("x2", x2); line.setAttribute("y2", y2);
        line.setAttribute("stroke", onPath ? "#f87171" : "#2a2d3a");
        line.setAttribute("stroke-width", onPath ? "2.5" : "1.5");
        line.setAttribute("marker-end", "url(#ag)");
        svg.appendChild(line);
      }

      for (const [name, pos] of Object.entries(NODE_POS)) {
        const rawSt = nodeStates[name] || "available";
        const st = name === expanding ? "expanding" : rawSt;
        const fill = NODE_COLORS[st] || "#6b7280";
        const tc = NODE_TEXT[st] || "#fff";
        const isExp = name === expanding;

        const g = document.createElementNS(NS, "g");

        if (isExp) {
          const ring = document.createElementNS(NS, "circle");
          ring.setAttribute("cx", pos.x); ring.setAttribute("cy", pos.y); ring.setAttribute("r", "22");
          ring.setAttribute("fill", fill); ring.setAttribute("opacity", "0.2");
          g.appendChild(ring);
        }

        const c = document.createElementNS(NS, "circle");
        c.setAttribute("cx", pos.x); c.setAttribute("cy", pos.y); c.setAttribute("r", "16");
        c.setAttribute("fill", fill);
        c.setAttribute("stroke", isExp ? "#fff" : "#1c1e27");
        c.setAttribute("stroke-width", isExp ? "2" : "1");
        g.appendChild(c);

        const t = document.createElementNS(NS, "text");
        t.setAttribute("x", pos.x); t.setAttribute("y", pos.y);
        t.setAttribute("text-anchor", "middle"); t.setAttribute("dominant-baseline", "central");
        t.setAttribute("font-size", "12"); t.setAttribute("font-weight", "700");
        t.setAttribute("font-family", "Space Mono, monospace");
        t.setAttribute("fill", tc);
        t.textContent = name;
        g.appendChild(t);

        if (st === "locked") {
          const lk = document.createElementNS(NS, "text");
          lk.setAttribute("x", pos.x + 12); lk.setAttribute("y", pos.y - 12);
          lk.setAttribute("font-size", "11"); lk.textContent = "🔒";
          g.appendChild(lk);
        }
        svg.appendChild(g);
      }
    }

    // ── Dibujo SVG — Grafo puzzle ──────────────────────────────────────────────
    function drawPuzzleGraph(nodeStates, gcostMap) {
      const svg = document.getElementById("puzzle-graph");
      svg.innerHTML = "";
      if (!Object.keys(nodeStates).length) {
        const t = document.createElementNS(NS, "text");
        t.setAttribute("x", "150"); t.setAttribute("y", "85");
        t.setAttribute("text-anchor", "middle"); t.setAttribute("dominant-baseline", "central");
        t.setAttribute("font-size", "11"); t.setAttribute("fill", "#555a72");
        t.setAttribute("font-family", "Space Mono, monospace");
        t.textContent = "sin puzzle activo";
        svg.appendChild(t);
        return;
      }
      svg.appendChild(makeArrow("ap"));

      for (const [a, b, cost] of PUZZLE_EDGES) {
        const pa = PUZZLE_POS[a], pb = PUZZLE_POS[b];
        if (!pa || !pb) continue;
        const dx = pb.x - pa.x, dy = pb.y - pa.y, len = Math.sqrt(dx * dx + dy * dy);
        const r = 14;
        const x1 = pa.x + dx / len * r, y1 = pa.y + dy / len * r;
        const x2 = pb.x - dx / len * (r + 3), y2 = pb.y - dy / len * (r + 3);
        const line = document.createElementNS(NS, "line");
        line.setAttribute("x1", x1); line.setAttribute("y1", y1);
        line.setAttribute("x2", x2); line.setAttribute("y2", y2);
        line.setAttribute("stroke", "#2a2d3a"); line.setAttribute("stroke-width", "1.5");
        line.setAttribute("marker-end", "url(#ap)");
        svg.appendChild(line);
        const mx = (x1 + x2) / 2, my = (y1 + y2) / 2;
        const lt = document.createElementNS(NS, "text");
        lt.setAttribute("x", mx + 5); lt.setAttribute("y", my - 4);
        lt.setAttribute("font-size", "9"); lt.setAttribute("fill", "#555a72");
        lt.setAttribute("font-family", "Space Mono, monospace");
        lt.textContent = cost;
        svg.appendChild(lt);
      }

      for (const [name, pos] of Object.entries(PUZZLE_POS)) {
        const st = nodeStates[name] || "available";
        const fill = NODE_COLORS[st] || "#6b7280";
        const tc = NODE_TEXT[st] || "#fff";
        const g = document.createElementNS(NS, "g");
        const c = document.createElementNS(NS, "circle");
        c.setAttribute("cx", pos.x); c.setAttribute("cy", pos.y); c.setAttribute("r", "14");
        c.setAttribute("fill", fill); c.setAttribute("stroke", "#1c1e27"); c.setAttribute("stroke-width", "1");
        g.appendChild(c);
        const t = document.createElementNS(NS, "text");
        t.setAttribute("x", pos.x); t.setAttribute("y", pos.y);
        t.setAttribute("text-anchor", "middle"); t.setAttribute("dominant-baseline", "central");
        t.setAttribute("font-size", "11"); t.setAttribute("font-weight", "700");
        t.setAttribute("font-family", "Space Mono, monospace");
        t.setAttribute("fill", tc); t.textContent = name;
        g.appendChild(t);
        if (gcostMap[name] !== undefined) {
          const gt = document.createElementNS(NS, "text");
          gt.setAttribute("x", pos.x); gt.setAttribute("y", pos.y + 24);
          gt.setAttribute("text-anchor", "middle"); gt.setAttribute("font-size", "9");
          gt.setAttribute("font-family", "Space Mono, monospace"); gt.setAttribute("fill", "#555a72");
          gt.textContent = "g=" + gcostMap[name];
          g.appendChild(gt);
        }
        svg.appendChild(g);
      }
    }

    // ── Lista de nodos ─────────────────────────────────────────────────────────
    function renderNodeList(nodeStates) {
      const el = document.getElementById("node-list");
      el.innerHTML = "";
      for (const n of ["A", "B", "C", "E", "G", "H", "I", "J", "K", "L", "M"]) {
        const st = nodeStates[n] || "available";
        const fill = NODE_COLORS[st] || "#6b7280";
        const div = document.createElement("div");
        div.className = "ni";
        div.innerHTML =
          `<span class="nd" style="background:${fill}"></span>
       <span class="nn">${n}</span>
       ${LOCKED_NODES.has(n) ? '<span class="pbadge">puzzle</span>' : ''}
       <span class="ns-label">${STATUS_LABELS[st] || st}</span>`;
        el.appendChild(div);
      }
    }

    // ── Utilidad log ───────────────────────────────────────────────────────────
    function appendLog(id, msg, cls) {
      const el = document.getElementById(id);
      const d = document.createElement("div");
      d.className = "ln " + (cls || "");
      d.textContent = msg;
      el.appendChild(d);
      el.scrollTop = el.scrollHeight;
    }