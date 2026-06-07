(function () {
  "use strict";

  const TOOLS = ["pen", "highlighter", "eraser", "line", "arrow", "rect", "circle", "text"];
  const COLORS = ["#1e1e1e","#ffffff","#ef4444","#f97316","#eab308","#22c55e","#3b82f6","#8b5cf6","#ec4899","#14b8a6","#f59e0b","#6b7280"];
  const SIZES  = [1, 3, 6, 12, 22];
  const MAX_HISTORY = 60;

  const state = {
    tool: "pen",
    color: COLORS[0],
    size: 3,
    fill: false,
    drawing: false,
    strokes: [],
    redoStack: [],
    current: null,
    boardId: null,
    saveUrl: null,
    deleteUrlBase: null,
    variant: "page",
  };

  let canvas, ctx, wrap, root, dpr;
  let textInput = null;
  let textInputPos = null;

  function init(opts) {
    opts = opts || {};
    wrap = document.querySelector(opts.wrap || "[data-wb-canvas-wrap]");
    if (!wrap) return;
    // The toolbar / color / size / etc. buttons are siblings of the wrap (not children),
    // so we need to scope queries to a wider root. Prefer an explicit [data-wb-root]
    // on a parent element; fall back to the wrap itself, then to document.
    root = wrap.closest("[data-wb-root]") || wrap.parentElement || document;
    state.variant = wrap.dataset.wbVariant || "page";
    state.boardId = wrap.dataset.wbBoardId ? parseInt(wrap.dataset.wbBoardId, 10) : null;
    state.saveUrl = wrap.dataset.wbSaveUrl || "/board/save/";
    // URL bases from templates look like "/delete/0/" — strip the trailing pk placeholder
    // so we can append a real id.
    state.deleteUrlBase = (wrap.dataset.wbDeleteUrlBase || "/board/delete/").replace(/\/\d+\/$/, "/");
    state.loadUrlBase   = (wrap.dataset.wbLoadUrlBase   || "/board/load/").replace(/\/\d+\/$/, "/");
    canvas = wrap.querySelector("[data-wb-canvas]");
    if (!canvas) return;
    dpr = Math.max(1, window.devicePixelRatio || 1);
    textInput = wrap.querySelector("[data-wb-text-input]");

    const alreadyBound = wrap.dataset.wbBound === "1";
    if (!alreadyBound) {
      bindUI();
      bindCanvas();
      bindKeyboard();
      bindResize();
      wrap.dataset.wbBound = "1";
    } else {
      // Re-running init() on the same wrap (e.g. focus overlay re-opens):
      // skip event re-binding and just refresh the canvas dimensions.
      resize();
    }
    setActiveTool(state.tool);
    setActiveColor(state.color);
    setActiveSize(state.size);

    if (state.boardId) loadDrawing(state.boardId);
    setStatus("Ready");
  }

  function resize() {
    if (!canvas) return;
    // Optional fixed canvas size (in CSS pixels). When the wrap sets
    // data-wb-fixed-width / data-wb-fixed-height the canvas backing
    // buffer is pinned to those dimensions regardless of how the
    // parent is scaled. Used by the focus overlay so the drawing
    // surface stays at the diagram's natural resolution even when
    // the user zooms in.
    const fixedW = wrap && wrap.dataset ? parseFloat(wrap.dataset.wbFixedWidth)  : NaN;
    const fixedH = wrap && wrap.dataset ? parseFloat(wrap.dataset.wbFixedHeight) : NaN;
    let w, h;
    if (Number.isFinite(fixedW) && Number.isFinite(fixedH) && fixedW > 0 && fixedH > 0) {
      w = fixedW;
      h = fixedH;
    } else {
      const r = canvas.getBoundingClientRect();
      if (r.width < 1 || r.height < 1) return;
      w = r.width;
      h = r.height;
    }
    canvas.width  = Math.max(1, Math.floor(w * dpr));
    canvas.height = Math.max(1, Math.floor(h * dpr));
    ctx = canvas.getContext("2d");
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    repaint();
  }

  function repaint() {
    if (!ctx) return;
    ctx.save();
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.restore();
    for (let i = 0; i < state.strokes.length; i++) drawStroke(state.strokes[i]);
    if (state.current) drawStroke(state.current);
  }

  function setStatus(msg) {
    if (!root) return;
    const el = root.querySelector("[data-wb-status]");
    if (el) el.textContent = msg;
  }

  function setTitleInState(title) {
    if (!root) return;
    const input = root.querySelector("[data-wb-title-input]");
    if (input) input.value = title || "";
    const label = root.querySelector("[data-wb-title-label]");
    if (label) label.textContent = title || "Untitled";
  }

  function setBoardId(id, title) {
    state.boardId = id;
    if (wrap) wrap.dataset.wbBoardId = id || "";
    setTitleInState(title);
  }

  function localPoint(evt) {
    const r = canvas.getBoundingClientRect();
    const src = (evt.touches && evt.touches[0]) || evt;
    return { x: src.clientX - r.left, y: src.clientY - r.top };
  }

  function setActiveTool(t) {
    state.tool = t;
    if (!root) return;
    root.querySelectorAll("[data-wb-tool]").forEach(function (b) {
      const v = b.dataset.wbTool;
      const isMatch = v === t;
      b.setAttribute("data-active", isMatch ? "true" : "false");
    });
  }
  function setActiveColor(c) {
    state.color = c;
    if (!root) return;
    root.querySelectorAll("[data-wb-color]").forEach(function (el) {
      const v = el.tagName === "SELECT" ? el.value : el.dataset.wbColor;
      const isMatch = v === c;
      if (el.tagName === "SELECT") el.value = c;
      else el.setAttribute("data-active", isMatch ? "true" : "false");
    });
  }
  function setActiveSize(s) {
    state.size = s;
    if (!root) return;
    root.querySelectorAll("[data-wb-size]").forEach(function (el) {
      const v = el.tagName === "SELECT" ? parseInt(el.value, 10) : parseInt(el.dataset.wbSize, 10);
      const isMatch = v === s;
      if (el.tagName === "SELECT") el.value = String(s);
      else el.setAttribute("data-active", isMatch ? "true" : "false");
    });
  }

  function bindUI() {
    root.querySelectorAll("[data-wb-tool]").forEach(function (btn) {
      btn.addEventListener("click", function () { setActiveTool(btn.dataset.wbTool); });
    });
    root.querySelectorAll("[data-wb-color]").forEach(function (el) {
      if (el.tagName === "SELECT") {
        el.addEventListener("change", function () { setActiveColor(el.value); });
      } else {
        el.addEventListener("click", function () { setActiveColor(el.dataset.wbColor); });
      }
    });
    root.querySelectorAll("[data-wb-size]").forEach(function (el) {
      if (el.tagName === "SELECT") {
        el.addEventListener("change", function () { setActiveSize(parseInt(el.value, 10)); });
      } else {
        el.addEventListener("click", function () { setActiveSize(parseInt(el.dataset.wbSize, 10)); });
      }
    });
    const fillBtn = root.querySelector("[data-wb-fill]");
    if (fillBtn) fillBtn.addEventListener("click", function () {
      state.fill = !state.fill;
      fillBtn.setAttribute("data-active", state.fill ? "true" : "false");
      fillBtn.setAttribute("aria-pressed", state.fill ? "true" : "false");
    });
    const undoBtn = root.querySelector("[data-wb-undo]");
    if (undoBtn) undoBtn.addEventListener("click", undo);
    const redoBtn = root.querySelector("[data-wb-redo]");
    if (redoBtn) redoBtn.addEventListener("click", redo);
    const clearBtn = root.querySelector("[data-wb-clear]");
    if (clearBtn) clearBtn.addEventListener("click", function () {
      if (state.strokes.length === 0) return;
      if (confirm("Clear the board?")) { state.strokes = []; state.redoStack = []; repaint(); }
    });
    const exportBtn = root.querySelector("[data-wb-export]");
    if (exportBtn) exportBtn.addEventListener("click", exportPNG);
    const saveBtn = root.querySelector("[data-wb-save]");
    if (saveBtn) saveBtn.addEventListener("click", save);
    const newBtn = root.querySelector("[data-wb-new]");
    if (newBtn) newBtn.addEventListener("click", function () {
      if (state.strokes.length && !confirm("Discard current drawing and start a new one?")) return;
      state.strokes = []; state.redoStack = []; state.current = null; state.drawing = false;
      setBoardId(null, "");
      setStatus("New drawing");
      repaint();
    });

    // Title input - sync value into state on input
    const titleInput = root.querySelector("[data-wb-title-input]");
    if (titleInput) {
      titleInput.addEventListener("input", function () {
        const label = root.querySelector("[data-wb-title-label]");
        if (label) label.textContent = titleInput.value || "Untitled";
      });
      titleInput.addEventListener("keydown", function (e) {
        if (e.key === "Enter") { e.preventDefault(); save(); }
      });
    }

    // Drawings list: load & delete
    root.querySelectorAll("[data-wb-load-id]").forEach(function (btn) {
      btn.addEventListener("click", function (e) {
        e.preventDefault();
        const id = parseInt(btn.dataset.wbLoadId, 10);
        if (!id) return;
        loadDrawing(id);
        setActiveItem(id);
      });
    });
    root.querySelectorAll("[data-wb-delete-id]").forEach(function (btn) {
      btn.addEventListener("click", function (e) {
        e.preventDefault();
        const id = parseInt(btn.dataset.wbDeleteId, 10);
        if (!id) return;
        if (!confirm("Delete this drawing?")) return;
        deleteDrawing(id);
      });
    });
  }

  function setActiveItem(id) {
    if (!root) return;
    root.querySelectorAll("[data-wb-load-id]").forEach(function (b) {
      b.classList.toggle("wb-item-active", parseInt(b.dataset.wbLoadId, 10) === id);
    });
  }

  function commitText() {
    if (!textInput || !textInputPos) return;
    const t = (textInput.value || "").trim();
    textInput.value = "";
    textInput.style.display = "none";
    const pos = textInputPos;
    textInputPos = null;
    if (t) {
      state.strokes.push({
        tool: "text", color: state.color, size: state.size,
        data: { x: pos.x, y: pos.y, text: t },
      });
      state.redoStack = [];
      if (state.strokes.length > MAX_HISTORY) state.strokes.shift();
      repaint();
    }
  }

  function startTextInput(pt) {
    if (!textInput) return;
    textInputPos = pt;
    const r = canvas.getBoundingClientRect();
    textInput.style.left = (pt.x) + "px";
    textInput.style.top  = (pt.y) + "px";
    textInput.style.display = "block";
    textInput.value = "";
    textInput.focus();
  }

  function bindCanvas() {
    const start = function (e) {
      e.preventDefault();
      const pt = localPoint(e);
      if (state.tool === "text") { startTextInput(pt); return; }
      if (state.tool === "pen" || state.tool === "highlighter" || state.tool === "eraser") {
        state.current = { tool: state.tool, color: state.color, size: state.size, data: { points: [pt] } };
      } else {
        state.current = { tool: state.tool, color: state.color, size: state.size, fill: state.fill,
                          data: { x1: pt.x, y1: pt.y, x2: pt.x, y2: pt.y } };
      }
      state.drawing = true;
    };
    const move = function (e) {
      if (!state.drawing || !state.current) return;
      e.preventDefault();
      const pt = localPoint(e);
      if (state.tool === "pen" || state.tool === "highlighter" || state.tool === "eraser") {
        state.current.data.points.push(pt);
      } else {
        state.current.data.x2 = pt.x;
        state.current.data.y2 = pt.y;
      }
      repaint();
    };
    const end = function (e) {
      if (!state.drawing || !state.current) return;
      if (e && e.preventDefault) e.preventDefault();
      state.strokes.push(state.current);
      state.current = null;
      state.drawing = false;
      state.redoStack = [];
      if (state.strokes.length > MAX_HISTORY) state.strokes.shift();
      repaint();
    };
    canvas.addEventListener("mousedown", start);
    canvas.addEventListener("mousemove", move);
    window.addEventListener("mouseup", end);
    canvas.addEventListener("mouseleave", function (e) { if (state.drawing) end(e); });
    canvas.addEventListener("touchstart", start, { passive: false });
    canvas.addEventListener("touchmove",  move,  { passive: false });
    canvas.addEventListener("touchend",   end);

    // Text input
    if (textInput) {
      textInput.addEventListener("keydown", function (e) {
        if (e.key === "Enter") { e.preventDefault(); commitText(); }
        else if (e.key === "Escape") { e.preventDefault(); textInput.value=""; textInput.style.display="none"; textInputPos = null; }
      });
      textInput.addEventListener("blur", function () { if (textInputPos) commitText(); });
    }
  }

  function bindKeyboard() {
    document.addEventListener("keydown", function (e) {
      const tag = e.target && e.target.tagName;
      if (tag === "INPUT" || tag === "TEXTAREA" || (e.target && e.target.isContentEditable)) {
        if (e.target && e.target.dataset && e.target.dataset.wbTextInput !== undefined) {
          // allow Esc/Enter for text input handled elsewhere
        } else {
          return;
        }
      }
      const k = e.key.toLowerCase();
      if ((e.ctrlKey || e.metaKey) && k === "z" && !e.shiftKey) { e.preventDefault(); undo(); return; }
      if ((e.ctrlKey || e.metaKey) && (k === "y" || (e.shiftKey && k === "z"))) { e.preventDefault(); redo(); return; }
      if ((e.ctrlKey || e.metaKey) && k === "s") { e.preventDefault(); save(); return; }
      const map = { p:"pen", h:"highlighter", e:"eraser", l:"line", a:"arrow", r:"rect", c:"circle", t:"text" };
      if (map[k]) {
        setActiveTool(map[k]);
      }
    });
  }

  function bindResize() {
    let t;
    window.addEventListener("resize", function () { clearTimeout(t); t = setTimeout(resize, 120); });
  }

  function drawStroke(s) {
    ctx.save();
    ctx.lineCap = "round";
    ctx.lineJoin = "round";
    if (s.tool === "highlighter") { ctx.globalAlpha = 0.35; ctx.globalCompositeOperation = "source-over"; }
    else if (s.tool === "eraser") { ctx.globalCompositeOperation = "destination-out"; ctx.strokeStyle = "#000000"; }
    else { ctx.globalCompositeOperation = "source-over"; ctx.strokeStyle = s.color; }
    ctx.fillStyle = s.color;
    ctx.lineWidth = s.size;

    switch (s.tool) {
      case "pen": case "highlighter": case "eraser": {
        const pts = s.data.points;
        if (!pts || !pts.length) break;
        ctx.beginPath();
        ctx.moveTo(pts[0].x, pts[0].y);
        for (let i = 1; i < pts.length; i++) ctx.lineTo(pts[i].x, pts[i].y);
        ctx.stroke();
        break;
      }
      case "line": {
        ctx.beginPath(); ctx.moveTo(s.data.x1, s.data.y1); ctx.lineTo(s.data.x2, s.data.y2); ctx.stroke();
        break;
      }
      case "arrow": {
        ctx.beginPath(); ctx.moveTo(s.data.x1, s.data.y1); ctx.lineTo(s.data.x2, s.data.y2); ctx.stroke();
        const ang = Math.atan2(s.data.y2 - s.data.y1, s.data.x2 - s.data.x1);
        const head = Math.max(8, s.size * 2.5);
        ctx.beginPath();
        ctx.moveTo(s.data.x2, s.data.y2);
        ctx.lineTo(s.data.x2 - head * Math.cos(ang - Math.PI/6), s.data.y2 - head * Math.sin(ang - Math.PI/6));
        ctx.lineTo(s.data.x2 - head * Math.cos(ang + Math.PI/6), s.data.y2 - head * Math.sin(ang + Math.PI/6));
        ctx.closePath(); ctx.fill();
        break;
      }
      case "rect": {
        const x = Math.min(s.data.x1, s.data.x2), y = Math.min(s.data.y1, s.data.y2);
        const w = Math.abs(s.data.x2 - s.data.x1), h = Math.abs(s.data.y2 - s.data.y1);
        if (s.fill) ctx.fillRect(x, y, w, h);
        else { ctx.beginPath(); ctx.rect(x, y, w, h); ctx.stroke(); }
        break;
      }
      case "circle": {
        const cx = (s.data.x1 + s.data.x2)/2, cy = (s.data.y1 + s.data.y2)/2;
        const rx = Math.abs(s.data.x2 - s.data.x1)/2, ry = Math.abs(s.data.y2 - s.data.y1)/2;
        ctx.beginPath(); ctx.ellipse(cx, cy, rx, ry, 0, 0, Math.PI*2);
        if (s.fill) ctx.fill(); else ctx.stroke();
        break;
      }
      case "text": {
        ctx.font = `${Math.max(12, s.size * 4)}px system-ui, sans-serif`;
        ctx.textBaseline = "top";
        ctx.fillText(s.data.text || "", s.data.x, s.data.y);
        break;
      }
    }
    ctx.restore();
  }

  function undo() {
    if (!state.strokes.length) return;
    state.redoStack.push(state.strokes.pop());
    repaint();
  }
  function redo() {
    if (!state.redoStack.length) return;
    state.strokes.push(state.redoStack.pop());
    repaint();
  }

  function getCookie(name) {
    const m = document.cookie.match(new RegExp("(?:^|; )" + name + "=([^;]*)"));
    return m ? decodeURIComponent(m[1]) : "";
  }

  function getTitle() {
    const input = root.querySelector("[data-wb-title-input]");
    return (input && input.value.trim()) || "Untitled";
  }

  async function save() {
    if (textInputPos) commitText();
    setStatus("Saving…");
    const dataUrl = canvas.toDataURL("image/png");
    try {
      const res = await fetch(state.saveUrl, {
        method: "POST",
        credentials: "same-origin",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCookie("csrftoken"),
          "X-Requested-With": "XMLHttpRequest",
        },
        body: JSON.stringify({ title: getTitle(), data_url: dataUrl, pk: state.boardId || null }),
      });
      const data = await res.json().catch(function () { return {}; });
      if (res.ok && data.ok) {
        setBoardId(data.id, data.title);
        setStatus("Saved (id=" + data.id + ")");
        prependOrUpdateListItem(data);
      } else {
        setStatus("Save failed: " + (data.error || res.status));
      }
    } catch (e) {
      setStatus("Save failed: " + e.message);
    }
  }

  function prependOrUpdateListItem(data) {
    const list = root.querySelector("[data-wb-drawings-list]");
    if (!list) return;
    let empty = list.querySelector("[data-wb-empty]");
    if (empty) empty.remove();
    let node = list.querySelector('[data-wb-load-id="' + data.id + '"]');
    if (!node) {
      node = document.createElement("div");
      node.dataset.wbLoadId = String(data.id);
      node.className = "wb-drawing-item";
      node.innerHTML =
        '<div class="wb-drawing-thumb"><div class="wb-drawing-thumb-inner">#' + data.id + '</div></div>' +
        '<div class="wb-drawing-meta">' +
          '<div class="wb-drawing-title">' + escapeHtml(data.title || "Untitled") + '</div>' +
          '<div class="wb-drawing-time">just now</div>' +
        '</div>' +
        '<div class="wb-drawing-actions">' +
          '<button type="button" class="wb-mini-btn" data-wb-load-id="' + data.id + '">Open</button>' +
          '<button type="button" class="wb-mini-btn wb-mini-btn-danger" data-wb-delete-id="' + data.id + '">Delete</button>' +
        '</div>';
      list.prepend(node);
      node.querySelector("[data-wb-load-id]").addEventListener("click", function (e) { e.preventDefault(); loadDrawing(data.id); setActiveItem(data.id); });
      node.querySelector("[data-wb-delete-id]").addEventListener("click", function (e) { e.preventDefault(); if (confirm("Delete?")) deleteDrawing(data.id); });
    } else {
      const t = node.querySelector(".wb-drawing-title");
      if (t) t.textContent = data.title || "Untitled";
    }
    setActiveItem(data.id);
  }

  function removeListItem(id) {
    const list = root.querySelector("[data-wb-drawings-list]");
    if (!list) return;
    const node = list.querySelector('[data-wb-load-id="' + id + '"]');
    if (node) node.remove();
    if (!list.children.length) {
      const empty = document.createElement("div");
      empty.dataset.wbEmpty = "true";
      empty.className = "wb-drawings-empty";
      empty.textContent = "No saved drawings yet.";
      list.appendChild(empty);
    }
  }

  async function loadDrawing(id) {
    setStatus("Loading…");
    try {
      const res = await fetch(state.loadUrlBase + id + "/", { credentials: "same-origin" });
      if (!res.ok) { setStatus("Load failed (" + res.status + ")"); return; }
      const data = await res.json();
      state.strokes = [];
      state.redoStack = [];
      state.current = null;
      state.drawing = false;
      setBoardId(data.id, data.title);
      setActiveItem(data.id);
      if (data.data_url) {
        const img = new Image();
        img.onload = function () {
          ctx.save();
          ctx.setTransform(1, 0, 0, 1, 0, 0);
          ctx.clearRect(0, 0, canvas.width, canvas.height);
          ctx.drawImage(img, 0, 0, canvas.clientWidth, canvas.clientHeight);
          ctx.restore();
          setStatus("Loaded \"" + (data.title || "Untitled") + "\"");
        };
        img.onerror = function () { setStatus("Failed to decode image"); };
        img.src = data.data_url;
      } else {
        repaint();
        setStatus("Loaded (empty)");
      }
    } catch (e) {
      setStatus("Load failed: " + e.message);
    }
  }

  async function deleteDrawing(id) {
    setStatus("Deleting…");
    try {
      const res = await fetch(state.deleteUrlBase + id + "/", {
        method: "POST",
        credentials: "same-origin",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCookie("csrftoken"),
          "X-Requested-With": "XMLHttpRequest",
        },
      });
      const data = await res.json().catch(function () { return {}; });
      if (res.ok && data.ok) {
        removeListItem(id);
        if (state.boardId === id) {
          state.strokes = []; state.redoStack = []; state.current = null; state.drawing = false;
          setBoardId(null, "");
          repaint();
        }
        setStatus("Deleted");
      } else {
        setStatus("Delete failed: " + (data.error || res.status));
      }
    } catch (e) {
      setStatus("Delete failed: " + e.message);
    }
  }

  function exportPNG() {
    const a = document.createElement("a");
    a.href = canvas.toDataURL("image/png");
    a.download = (getTitle() || "whiteboard").replace(/[^a-z0-9\-_]+/gi, "_") + ".png";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  }

  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return ({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"})[c];
    });
  }

  window.Whiteboard = {
    init: init, save: save, loadDrawing: loadDrawing, deleteDrawing: deleteDrawing,
    exportPNG: exportPNG, undo: undo, redo: redo, clear: function () { state.strokes=[]; state.redoStack=[]; repaint(); },
    refresh: function () { resize(); repaint(); },
    state: state,
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function () { init({}); });
  } else {
    init({});
  }
})();
