/* Module Focus + Freeze & draw
 * ─────────────────────────────
 *  Two diagram-toolbar actions:
 *    data-focus-toggle       — open / close the focus overlay
 *    data-whiteboard-toggle  — freeze the diagram and enable the
 *                              whiteboard engine on top of it
 *
 *  Plus, once the overlay is open:
 *    data-zoom-in / -out / -fit / -reset — zoom controls
 *    data-grid-toggle                     — toggle the grid overlay
 *    data-focus-pan                       — enter pan mode (drag stage)
 *    data-focus-recent-toggle             — open the recent-annotations drawer
 *    data-focus-export                    — export the combined PNG
 *    data-focus-help / -close             — show / hide keyboard shortcuts
 *    data-toolbar-collapse                — collapse / expand the toolbar
 *    [data-focus-toolbar] handle          — drag to move the toolbar
 *
 *  The whiteboard engine (whiteboard.js) is driven the same way the
 *  standalone /board/ page uses it — we just point it at the
 *  [data-wb-canvas-wrap] inside the stage and at the per-module
 *  annotation save/list URLs.
 *
 *  State is local (closure-scope) so it never collides with the rest
 *  of the module page.
 */
(function () {
  "use strict";

  // ─── module state ──────────────────────────────────────────
  const state = {
    // zoom / pan
    scale: 1,
    panX: 0,
    panY: 0,
    minScale: 0.1,
    maxScale: 8,
    // pan drag (when pan tool active or middle-click)
    panning: false,
    panStart: null,
    // grid
    gridOn: false,
    // pan tool
    panTool: false,
    // collapse
    toolbarCollapsed: false,
    // position of floating toolbar (px from parent top-left)
    toolbarX: 16,
    toolbarY: 16,
    // recent annotations
    recent: [],
    recentLoaded: false,
  };

  // ─── helpers ───────────────────────────────────────────────
  function $overlay() { return document.querySelector("[data-focus-overlay]"); }
  function $stage()   { return $overlay() && $overlay().querySelector("[data-focus-stage]"); }
  function $content() { return $overlay() && $overlay().querySelector("[data-stage-content]"); }
  function $canvasWrap() { return $overlay() && $overlay().querySelector("[data-wb-canvas-wrap]"); }
  function $canvas()  { return $overlay() && $overlay().querySelector("[data-wb-canvas]"); }
  function $backdrop(){ return $overlay() && $overlay().querySelector("[data-focus-backdrop]"); }
  function $toolbar() { return $overlay() && $overlay().querySelector("[data-focus-toolbar]"); }
  function $handle()  { return $overlay() && $overlay().querySelector("[data-toolbar-handle]"); }
  function $body()    { return $overlay() && $overlay().querySelector("[data-toolbar-body]"); }
  function $collapse() { return $overlay() && $overlay().querySelector("[data-toolbar-collapse]"); }
  function $zoomPercent() { return $overlay() && $overlay().querySelector("[data-zoom-percent]"); }
  function $grid()    { return $overlay() && $overlay().querySelector("[data-focus-grid]"); }
  function $recent()  { return $overlay() && $overlay().querySelector("[data-focus-recent]"); }
  function $recentList() { return $overlay() && $overlay().querySelector("[data-focus-recent-list]"); }
  function $page()    { return document.querySelector("[data-module-page]"); }
  function $plotlyDiv() {
    const page = $page();
    const mod = (page && page.dataset && page.dataset.module) || "";
    return document.getElementById("plot-" + mod);
  }

  function getNaturalSize() {
    const o = $overlay();
    return {
      w: parseFloat(o && o.dataset && o.dataset.naturalWidth) || 1600,
      h: parseFloat(o && o.dataset && o.dataset.naturalHeight) || 900,
    };
  }

  function getStageSize() {
    const s = $stage();
    if (!s) return { w: 0, h: 0 };
    const r = s.getBoundingClientRect();
    return { w: r.width, h: r.height };
  }

  // ─── zoom / pan ────────────────────────────────────────────
  function applyTransform() {
    const el = $content();
    if (!el) return;
    el.style.transform = `translate(${state.panX}px, ${state.panY}px) scale(${state.scale})`;
    const pct = $zoomPercent();
    if (pct) pct.textContent = Math.round(state.scale * 100) + "%";
  }

  function zoomTo(scale, cx, cy) {
    const oldScale = state.scale;
    const s = Math.max(state.minScale, Math.min(state.maxScale, scale));
    if (s === oldScale) return;
    // Zoom around the given point (in stage CSS pixels) so the
    // point under the cursor stays put. If no point given, zoom
    // around the stage center.
    let pivot = { x: cx, y: cy };
    if (pivot.x == null) {
      const st = getStageSize();
      pivot = { x: st.w / 2, y: st.h / 2 };
    }
    // The diagram's content center is at (stage.w/2 + panX, stage.h/2 + panY)
    // in stage CSS coordinates. Convert pivot to that space.
    const st = getStageSize();
    const contentCenterX = st.w / 2 + state.panX;
    const contentCenterY = st.h / 2 + state.panY;
    // Solve for the new pan such that the diagram's center is
    // still under the cursor after the scale change.
    const ratio = s / oldScale;
    state.panX = (pivot.x - contentCenterX) * (1 - ratio) + (state.panX * ratio);
    state.panY = (pivot.y - contentCenterY) * (1 - ratio) + (state.panY * ratio);
    state.scale = s;
    applyTransform();
    // Re-resize the canvas so the backing buffer matches the new
    // scaled display (the engine pins to the natural size; we
    // override that for the zoom-in case by calling resize via
    // the engine's helper, but keep the backing size at the
    // natural resolution for crisp drawing.)
    // We just refresh; the engine's own resize is pinned to the
    // fixed size we set, so strokes stay at the natural res.
    if (window.Whiteboard && typeof Whiteboard.refresh === "function") {
      Whiteboard.refresh();
    }
  }

  function zoomIn()  { zoomTo(state.scale * 1.25); }
  function zoomOut() { zoomTo(state.scale / 1.25); }
  function zoomReset() { state.panX = 0; state.panY = 0; state.scale = 1; applyTransform(); if (window.Whiteboard && Whiteboard.refresh) Whiteboard.refresh(); }

  function zoomFit() {
    const st = getStageSize();
    const { w, h } = getNaturalSize();
    if (!st.w || !st.h || !w || !h) return;
    const sx = (st.w - 24) / w;  // 12px padding each side
    const sy = (st.h - 24) / h;
    state.scale = Math.max(state.minScale, Math.min(state.maxScale, Math.min(sx, sy)));
    state.panX = 0;
    state.panY = 0;
    applyTransform();
    if (window.Whiteboard && Whiteboard.refresh) Whiteboard.refresh();
  }

  // ─── pan via drag (when pan tool is active, or middle mouse, or space) ───
  function startPan(evt) {
    if (evt.button !== undefined && evt.button !== 0 && evt.button !== 1) return;
    state.panning = true;
    state.panStart = {
      x: evt.clientX,
      y: evt.clientY,
      panX: state.panX,
      panY: state.panY,
    };
    evt.preventDefault();
  }
  function movePan(evt) {
    if (!state.panning) return;
    const dx = evt.clientX - state.panStart.x;
    const dy = evt.clientY - state.panStart.y;
    state.panX = state.panStart.panX + dx;
    state.panY = state.panStart.panY + dy;
    applyTransform();
  }
  function endPan() { state.panning = false; }

  // ─── freeze the current diagram to PNG ─────────────────────
  function freezeCurrentDiagram() {
    return new Promise(function (resolve) {
      const gd = $plotlyDiv();
      const img = $backdrop();
      if (!gd || !window.Plotly || typeof Plotly.toImage !== "function") {
        if (img) img.hidden = true;
        resolve(null);
        return;
      }
      Plotly.toImage(gd, { format: "png", width: 1600, height: 900 })
        .then(function (dataUrl) {
          if (img) {
            img.src = dataUrl;
            img.hidden = false;
            img.draggable = false;
          }
          resolve(dataUrl);
        })
        .catch(function () {
          if (img) img.hidden = true;
          resolve(null);
        });
    });
  }

  // ─── overlay open / close ──────────────────────────────────
  function openOverlay() {
    const overlay = $overlay();
    if (!overlay) return;
    overlay.hidden = false;
    document.body.classList.add("focus-open");
    if (overlay.requestFullscreen) {
      overlay.requestFullscreen().catch(function () { /* ignored */ });
    }
    // Fit zoom on open (defer to next frame so stage has dimensions)
    requestAnimationFrame(zoomFit);
  }

  function closeOverlay() {
    const overlay = $overlay();
    if (!overlay) return;
    overlay.hidden = true;
    document.body.classList.remove("focus-open");
    if (document.fullscreenElement === overlay && document.exitFullscreen) {
      document.exitFullscreen().catch(function () { /* ignored */ });
    }
  }

  function isOverlayOpen() {
    const overlay = $overlay();
    return !!(overlay && !overlay.hidden);
  }

  // ─── handlers ──────────────────────────────────────────────
  function onFocusToggle(evt) {
    if (evt) evt.preventDefault();
    if (isOverlayOpen()) {
      closeOverlay();
    } else {
      freezeCurrentDiagram().then(function () {
        openOverlay();
        // Pure Focus: hide canvas + toolbar (we just want to view
        // the diagram). The toolbar is still draggable in this
        // mode; the user can collapse it or hit the "Freeze &
        // draw" button (which re-uses data-whiteboard-toggle) to
        // enable the canvas.
        const canvasWrap = $canvasWrap();
        const toolbar = $toolbar();
        if (canvasWrap) canvasWrap.style.display = "none";
        if (toolbar) toolbar.style.display = "";
        // Reset pan/zoom + toolbar position to defaults
        state.panX = 0; state.panY = 0; state.scale = 1;
        applyTransform();
        resetToolbarPosition();
      });
    }
  }

  function onWhiteboardToggle(evt) {
    if (evt) evt.preventDefault();
    const overlay = $overlay();
    if (!overlay) return;
    const canvasWrap = $canvasWrap();
    const toolbar = $toolbar();
    if (canvasWrap) canvasWrap.style.display = "";
    if (toolbar) toolbar.style.display = "";
    const wasOpen = isOverlayOpen();
    freezeCurrentDiagram().then(function () {
      if (!wasOpen) openOverlay();
      requestAnimationFrame(function () {
        if (window.Whiteboard && typeof Whiteboard.init === "function") {
          Whiteboard.init({ wrap: canvasWrap });
          if (typeof Whiteboard.refresh === "function") Whiteboard.refresh();
        }
        zoomFit();
        // Auto-load the most recent annotation as a friendly default.
        if (!state.recentLoaded) {
          state.recentLoaded = true;
          loadRecentList().then(function (rows) {
            if (rows && rows.length) loadAnnotationIntoBoard(rows[0]);
          });
        }
      });
    });
  }

  // ─── zoom handlers ─────────────────────────────────────────
  function onZoomIn()  { zoomIn(); }
  function onZoomOut() { zoomOut(); }
  function onZoomFit() { zoomFit(); }
  function onZoomReset() { zoomReset(); }

  // ─── grid ──────────────────────────────────────────────────
  function setGrid(on) {
    state.gridOn = !!on;
    const g = $grid();
    if (g) g.hidden = !state.gridOn;
    // Sync any toolbar button that targets the grid toggle
    document.querySelectorAll("[data-grid-toggle]").forEach(function (b) {
      b.setAttribute("data-active", state.gridOn ? "true" : "false");
    });
  }
  function onGridToggle() { setGrid(!state.gridOn); }

  // ─── pan tool toggle ───────────────────────────────────────
  function setPanTool(on) {
    state.panTool = !!on;
    document.querySelectorAll("[data-focus-pan]").forEach(function (b) {
      b.setAttribute("data-active", state.panTool ? "true" : "false");
    });
    const wrap = $canvasWrap();
    if (wrap) wrap.style.cursor = state.panTool ? "grab" : "";
  }
  function onPanToggle() { setPanTool(!state.panTool); }

  // ─── toolbar collapse ──────────────────────────────────────
  function setToolbarCollapsed(c) {
    state.toolbarCollapsed = !!c;
    const t = $toolbar();
    if (t) t.classList.toggle("collapsed", state.toolbarCollapsed);
    if ($collapse()) $collapse().textContent = state.toolbarCollapsed ? "+" : "−";
  }
  function onToolbarCollapse() { setToolbarCollapsed(!state.toolbarCollapsed); }

  // ─── toolbar dragging ──────────────────────────────────────
  function resetToolbarPosition() {
    const t = $toolbar();
    if (!t) return;
    state.toolbarX = 16; state.toolbarY = 16;
    t.style.left = state.toolbarX + "px";
    t.style.top = state.toolbarY + "px";
  }
  function bindToolbarDrag() {
    const handle = $handle();
    const toolbar = $toolbar();
    if (!handle || !toolbar) return;
    if (handle.dataset.dragBound === "1") return;
    handle.dataset.dragBound = "1";
    let dragging = false;
    let startX = 0, startY = 0, startLeft = 0, startTop = 0;
    let parentRect = null;
    handle.addEventListener("mousedown", function (e) {
      if (e.target.closest("[data-toolbar-collapse]")) return;
      dragging = true;
      startX = e.clientX; startY = e.clientY;
      const pr = toolbar.parentElement.getBoundingClientRect();
      const tr = toolbar.getBoundingClientRect();
      startLeft = tr.left - pr.left;
      startTop = tr.top - pr.top;
      parentRect = pr;
      e.preventDefault();
    });
    document.addEventListener("mousemove", function (e) {
      if (!dragging || !parentRect) return;
      const dx = e.clientX - startX;
      const dy = e.clientY - startY;
      let nx = startLeft + dx;
      let ny = startTop + dy;
      // Clamp to the parent
      const tr = toolbar.getBoundingClientRect();
      const w = tr.width, h = tr.height;
      nx = Math.max(0, Math.min(parentRect.width - w - 4, nx));
      ny = Math.max(0, Math.min(parentRect.height - h - 4, ny));
      toolbar.style.left = nx + "px";
      toolbar.style.top = ny + "px";
      state.toolbarX = nx; state.toolbarY = ny;
    });
    document.addEventListener("mouseup", function () { dragging = false; parentRect = null; });
  }

  // ─── color picker ──────────────────────────────────────────
  function bindColorPicker() {
    const picker = $overlay() && $overlay().querySelector("[data-wb-color-picker]");
    if (!picker || picker.dataset.bound === "1") return;
    picker.dataset.bound = "1";
    picker.addEventListener("input", function () {
      const c = picker.value;
      // Mark the picker as active and deactivate all preset swatches.
      document.querySelectorAll("[data-wb-color]").forEach(function (s) {
        s.setAttribute("data-active", "false");
      });
      picker.parentElement.setAttribute("data-active", "true");
      // Sync the picker swatch (we keep the conic gradient for
      // discoverability; the actual selected color goes into state).
      // We dispatch a custom event the rest of the engine uses to
      // update its color state.
      if (window.Whiteboard && window.Whiteboard.state) {
        window.Whiteboard.state.color = c;
        // Trigger a synthetic click on a fake color swatch by
        // setting the active color directly via the engine API.
        // The engine exposes setActiveColor only inside its closure,
        // so the cleanest hook is to set the swatch data-active
        // then dispatch a click on the picker wrapper. The engine
        // binds only to [data-wb-color] (preset swatches) and not
        // to a custom color input, so we manually update the
        // color via the picker's parent swatch styling.
      }
      // Update the picker swatch to show the chosen color
      const sw = picker.parentElement.querySelector("[data-wb-color-picker-swatch]");
      if (sw) sw.style.background = c;
    });
  }

  // ─── recent annotations ────────────────────────────────────
  function setRecentOpen(o) {
    const r = $recent();
    if (!r) return;
    r.hidden = !o;
    if (o && !state.recentLoaded) {
      state.recentLoaded = true;
      loadRecentList();
    }
  }
  function onRecentToggle() {
    const r = $recent();
    if (!r) return;
    setRecentOpen(r.hidden);
  }

  function getCookie(name) {
    const m = document.cookie.match(new RegExp("(?:^|; )" + name + "=([^;]*)"));
    return m ? decodeURIComponent(m.group(1)) : "";
  }

  function loadRecentList() {
    const overlay = $overlay();
    if (!overlay) return Promise.resolve([]);
    const url = overlay.dataset.annotationListUrl;
    if (!url) return Promise.resolve([]);
    return fetch(url, { credentials: "same-origin" })
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (data) {
        if (!data || !data.ok) return [];
        state.recent = data.drawings || [];
        renderRecentList();
        return state.recent;
      })
      .catch(function () { return []; });
  }

  function renderRecentList() {
    const list = $recentList();
    if (!list) return;
    list.innerHTML = "";
    if (!state.recent.length) {
      const empty = document.createElement("div");
      empty.className = "focus-recent-empty";
      empty.setAttribute("data-focus-recent-empty", "");
      empty.textContent = "No saved annotations yet — draw something and hit Save.";
      list.appendChild(empty);
      return;
    }
    state.recent.forEach(function (d) {
      const item = document.createElement("div");
      item.className = "focus-recent-item";
      const thumb = document.createElement("div");
      thumb.className = "focus-recent-thumb";
      if (d.image_url) {
        const img = document.createElement("img");
        img.src = d.image_url;
        img.alt = "";
        thumb.appendChild(img);
      } else {
        thumb.textContent = "#" + d.id;
      }
      const meta = document.createElement("div");
      meta.className = "focus-recent-meta";
      const t = document.createElement("div");
      t.className = "focus-recent-title";
      t.textContent = d.title || "Untitled";
      const time = document.createElement("div");
      time.className = "focus-recent-time";
      time.textContent = d.updated_at ? new Date(d.updated_at).toLocaleString() : "";
      meta.appendChild(t); meta.appendChild(time);
      const actions = document.createElement("div");
      actions.className = "focus-recent-actions";
      const open = document.createElement("button");
      open.type = "button";
      open.className = "focus-recent-action";
      open.textContent = "Open";
      open.addEventListener("click", function (e) {
        e.stopPropagation();
        loadAnnotationIntoBoard(d);
        setRecentOpen(false);
      });
      const del = document.createElement("button");
      del.type = "button";
      del.className = "focus-recent-action focus-recent-action-danger";
      del.textContent = "Del";
      del.addEventListener("click", function (e) {
        e.stopPropagation();
        if (!confirm("Delete '" + (d.title || "Untitled") + "'?")) return;
        deleteAnnotation(d.id);
      });
      actions.appendChild(open); actions.appendChild(del);
      item.appendChild(thumb); item.appendChild(meta); item.appendChild(actions);
      list.appendChild(item);
    });
  }

  function loadAnnotationIntoBoard(d) {
    // Set the engine's strokes from the JSON we saved earlier and
    // repaint. We bypass the engine's PNG path so the load is lossless.
    if (!window.Whiteboard) return;
    const s = window.Whiteboard.state;
    if (!s) return;
    s.strokes = Array.isArray(d.strokes) ? d.strokes : [];
    s.redoStack = [];
    s.current = null;
    s.drawing = false;
    s.boardId = d.id;
    // Mark title in the title input
    const ti = $overlay().querySelector("[data-wb-title-input]");
    if (ti) ti.value = d.title || "";
    // Mark wrap's board id so subsequent saves update this row.
    const wrap = $canvasWrap();
    if (wrap) wrap.dataset.wbBoardId = d.id;
    if (typeof window.Whiteboard.refresh === "function") {
      window.Whiteboard.refresh();
    }
  }

  function deleteAnnotation(id) {
    const overlay = $overlay();
    if (!overlay) return;
    const list = overlay.dataset.annotationListUrl || "";
    const deleteUrl = (overlay.querySelector("[data-wb-canvas-wrap]") || {}).dataset
      ? (overlay.querySelector("[data-wb-canvas-wrap]").dataset.wbDeleteUrlBase || "")
      : "";
    const url = (deleteUrl || "").replace(/\/0\/$/, "/") + id + "/";
    fetch(url, {
      method: "POST",
      credentials: "same-origin",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie("csrftoken"),
        "X-Requested-With": "XMLHttpRequest",
      },
      body: JSON.stringify({}),
    })
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (data) {
        if (data && data.ok) {
          state.recent = state.recent.filter(function (x) { return x.id !== id; });
          renderRecentList();
        }
      })
      .catch(function () { /* ignore */ });
  }

  // ─── export combined PNG (backdrop + canvas) ───────────────
  function onExport() {
    const bd = $backdrop();
    const cv = $canvas();
    if (!bd || bd.hidden || !cv) {
      // No backdrop or no canvas — just export the canvas alone
      if (window.Whiteboard && window.Whiteboard.exportPNG) window.Whiteboard.exportPNG();
      return;
    }
    const img = new Image();
    img.onload = function () {
      const out = document.createElement("canvas");
      out.width = img.naturalWidth;
      out.height = img.naturalHeight;
      const ctx = out.getContext("2d");
      ctx.drawImage(img, 0, 0);
      // Draw the strokes canvas on top (scaled to the natural size)
      ctx.drawImage(cv, 0, 0, img.naturalWidth, img.naturalHeight);
      const a = document.createElement("a");
      a.href = out.toDataURL("image/png");
      const titleEl = $overlay().querySelector("[data-wb-title-input]");
      a.download = (titleEl && titleEl.value
        ? titleEl.value
        : ($page() && $page().dataset && $page().dataset.module) || "annotation"
      ).replace(/[^a-z0-9\-_]+/gi, "_") + ".png";
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    };
    img.onerror = function () {
      if (window.Whiteboard && window.Whiteboard.exportPNG) window.Whiteboard.exportPNG();
    };
    img.src = bd.src;
  }

  // ─── help overlay ──────────────────────────────────────────
  function setHelpOpen(o) {
    const h = $overlay() && $overlay().querySelector("[data-focus-help-overlay]");
    if (!h) return;
    h.hidden = !o;
  }
  function onHelpToggle() {
    const h = $overlay() && $overlay().querySelector("[data-focus-help-overlay]");
    if (!h) return;
    setHelpOpen(h.hidden);
  }

  // ─── engine patches ────────────────────────────────────────
  // The whiteboard engine's `save()` posts to state.saveUrl with the
  // canvas's PNG only. For the focus overlay we also want the stroke
  // list (so the user can re-edit later) and the backdrop (so the
  // server can compose a thumbnail). We hook the save button via a
  // capturing listener that runs BEFORE the engine's listener and,
  // if it can build a full payload, prevents the engine's default
  // save. Otherwise, the engine's save proceeds as usual.
  function bindSaveHook() {
    const overlay = $overlay();
    if (!overlay) return;
    const saveBtn = overlay.querySelector("[data-wb-save]");
    if (!saveBtn || saveBtn.dataset.hookBound === "1") return;
    saveBtn.dataset.hookBound = "1";
    saveBtn.addEventListener("click", function (e) {
      // Only intercept if the user is on a module page (we have
      // an annotation-save URL) and we have a backdrop.
      const saveUrl = overlay.dataset.annotationSaveUrl;
      const bd = $backdrop();
      if (!saveUrl || !bd || bd.hidden || !window.Whiteboard) return;  // let engine handle
      e.stopImmediatePropagation();
      e.preventDefault();
      const s = window.Whiteboard.state;
      const ti = overlay.querySelector("[data-wb-title-input]");
      const wrap = $canvasWrap();
      const payload = {
        title: ti && ti.value ? ti.value : "",
        strokes: s ? s.strokes : [],
        background_data_url: bd.src,
        pk: (wrap && wrap.dataset.wbBoardId) ? parseInt(wrap.dataset.wbBoardId, 10) : null,
      };
      const status = overlay.querySelector("[data-wb-status]");
      if (status) status.textContent = "Saving…";
      fetch(saveUrl, {
        method: "POST",
        credentials: "same-origin",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCookie("csrftoken"),
          "X-Requested-With": "XMLHttpRequest",
        },
        body: JSON.stringify(payload),
      })
        .then(function (r) { return r.json().then(function (d) { return { ok: r.ok, data: d }; }); })
        .then(function (out) {
          if (!out.ok || !out.data.ok) {
            if (status) status.textContent = "Save failed: " + (out.data && out.data.error || "error");
            return;
          }
          if (status) status.textContent = "Saved (id=" + out.data.id + ")";
          if (wrap) wrap.dataset.wbBoardId = out.data.id;
          // Update the recent list cache
          state.recentLoaded = true;
          loadRecentList();
        })
        .catch(function (err) {
          if (status) status.textContent = "Save failed: " + err.message;
        });
    }, true /* capturing, so it runs before the engine's bubble listener */);
  }

  // ─── keyboard shortcuts inside the overlay ─────────────────
  function onKeydown(evt) {
    if (!isOverlayOpen()) return;
    const tag = evt.target && evt.target.tagName;
    const isTyping = tag === "INPUT" || tag === "TEXTAREA" || (evt.target && evt.target.isContentEditable);
    // Esc closes the overlay no matter what (even when typing in
    // a text input, the user can press Esc to dismiss it).
    if (evt.key === "Escape") {
      // If help or recent is open, close that first.
      const h = $overlay() && $overlay().querySelector("[data-focus-help-overlay]");
      const r = $recent();
      if (h && !h.hidden) { setHelpOpen(false); evt.preventDefault(); return; }
      if (r && !r.hidden) { setRecentOpen(false); evt.preventDefault(); return; }
      evt.preventDefault();
      closeOverlay();
      return;
    }
    if (isTyping && evt.target.dataset && evt.target.dataset.wbTextInput !== undefined) {
      // Text tool input is part of the engine's flow; let it through.
    } else if (isTyping) {
      return;
    }
    // Global shortcuts (only when not typing in the title input,
    // for example).
    if (evt.ctrlKey || evt.metaKey) {
      const k = (evt.key || "").toLowerCase();
      if (k === "z" && !evt.shiftKey) { return; } // engine handles
      if (k === "y" || (evt.shiftKey && k === "z")) { return; }
      if (k === "s") { evt.preventDefault(); return; }
      if (k === "=" || k === "+") { evt.preventDefault(); zoomIn(); return; }
      if (k === "-" || k === "_") { evt.preventDefault(); zoomOut(); return; }
      if (k === "0") { evt.preventDefault(); zoomReset(); return; }
    }
    if (evt.altKey) return;
    const k = (evt.key || "").toLowerCase();
    // Single-key shortcuts. Skip if a modifier is held.
    if (evt.ctrlKey || evt.metaKey) return;
    if (k === "0") { zoomReset(); return; }
    if (k === "f") { zoomFit(); return; }
    if (k === "g") { setGrid(!state.gridOn); return; }
    if (k === "c") { setToolbarCollapsed(!state.toolbarCollapsed); return; }
    if (k === "m") { setPanTool(!state.panTool); return; }
    if (k === "?") { onHelpToggle(); return; }
  }

  // ─── wheel zoom (Ctrl+wheel) ───────────────────────────────
  function onWheel(evt) {
    if (!isOverlayOpen()) return;
    // Only zoom when Ctrl/Cmd is held, so regular wheel scroll on
    // touchpads doesn't yank the diagram.
    if (!(evt.ctrlKey || evt.metaKey)) return;
    evt.preventDefault();
    const stage = $stage();
    if (!stage) return;
    const rect = stage.getBoundingClientRect();
    const cx = evt.clientX - rect.left;
    const cy = evt.clientY - rect.top;
    const dir = evt.deltaY < 0 ? 1.15 : 1 / 1.15;
    zoomTo(state.scale * dir, cx, cy);
  }

  // ─── bind once on load ─────────────────────────────────────
  function bind() {
    // Toolbar buttons (data-focus-toggle and data-whiteboard-toggle
    // are also in the overlay's own header so they can be reached
    // from inside the overlay).
    document.querySelectorAll("[data-focus-toggle]").forEach(function (b) {
      if (b.dataset.focusBound === "1") return;
      b.addEventListener("click", onFocusToggle);
      b.dataset.focusBound = "1";
    });
    document.querySelectorAll("[data-whiteboard-toggle]").forEach(function (b) {
      if (b.dataset.focusBound === "1") return;
      b.addEventListener("click", onWhiteboardToggle);
      b.dataset.focusBound = "1";
    });
    document.querySelectorAll("[data-zoom-in]").forEach(function (b) {
      if (b.dataset.focusBound === "1") return;
      b.addEventListener("click", onZoomIn);
      b.dataset.focusBound = "1";
    });
    document.querySelectorAll("[data-zoom-out]").forEach(function (b) {
      if (b.dataset.focusBound === "1") return;
      b.addEventListener("click", onZoomOut);
      b.dataset.focusBound = "1";
    });
    document.querySelectorAll("[data-zoom-fit]").forEach(function (b) {
      if (b.dataset.focusBound === "1") return;
      b.addEventListener("click", onZoomFit);
      b.dataset.focusBound = "1";
    });
    document.querySelectorAll("[data-zoom-reset]").forEach(function (b) {
      if (b.dataset.focusBound === "1") return;
      b.addEventListener("click", onZoomReset);
      b.dataset.focusBound = "1";
    });
    document.querySelectorAll("[data-grid-toggle]").forEach(function (b) {
      if (b.dataset.focusBound === "1") return;
      b.addEventListener("click", onGridToggle);
      b.dataset.focusBound = "1";
    });
    document.querySelectorAll("[data-focus-pan]").forEach(function (b) {
      if (b.dataset.focusBound === "1") return;
      b.addEventListener("click", onPanToggle);
      b.dataset.focusBound = "1";
    });
    document.querySelectorAll("[data-focus-recent-toggle]").forEach(function (b) {
      if (b.dataset.focusBound === "1") return;
      b.addEventListener("click", onRecentToggle);
      b.dataset.focusBound = "1";
    });
    document.querySelectorAll("[data-focus-export]").forEach(function (b) {
      if (b.dataset.focusBound === "1") return;
      b.addEventListener("click", onExport);
      b.dataset.focusBound = "1";
    });
    document.querySelectorAll("[data-focus-help]").forEach(function (b) {
      if (b.dataset.focusBound === "1") return;
      b.addEventListener("click", onHelpToggle);
      b.dataset.focusBound = "1";
    });
    document.querySelectorAll("[data-focus-help-close]").forEach(function (b) {
      if (b.dataset.focusBound === "1") return;
      b.addEventListener("click", function () { setHelpOpen(false); });
      b.dataset.focusBound = "1";
    });
    document.querySelectorAll("[data-toolbar-collapse]").forEach(function (b) {
      if (b.dataset.focusBound === "1") return;
      b.addEventListener("click", onToolbarCollapse);
      b.dataset.focusBound = "1";
    });

    bindToolbarDrag();
    bindColorPicker();
    bindSaveHook();

    document.addEventListener("keydown", onKeydown);
    const stage = $stage();
    if (stage) {
      stage.addEventListener("wheel", onWheel, { passive: false });
      // Pan via drag on the dark area (i.e. on the stage element
      // itself, not on the canvas). The canvas consumes its own
      // mouse events for drawing.
      stage.addEventListener("mousedown", function (e) {
        // Only pan if the click is on the stage itself, not on
        // a child (toolbar, recent panel, help, etc.)
        if (e.target !== stage) return;
        startPan(e);
      });
      document.addEventListener("mousemove", movePan);
      document.addEventListener("mouseup", endPan);
    }

    // Pull the formula + title into the overlay for context.
    const page = $page();
    const overlay = $overlay();
    if (page && overlay) {
      const f = overlay.querySelector("[data-focus-formula]");
      if (f && page.dataset.formula) f.textContent = page.dataset.formula;
      const t = overlay.querySelector("[data-focus-title]");
      if (t && page.dataset.module) t.textContent =
        (page.dataset.module || "module").replace(/^./, function (c) { return c.toUpperCase(); });
    }

    applyTransform();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", bind);
  } else {
    bind();
  }
})();
