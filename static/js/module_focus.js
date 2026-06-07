/* Module Focus + Freeze & draw
 * ─────────────────────────────
 *  Two diagram-toolbar actions:
 *    data-focus-toggle       — open / close full-screen focus overlay
 *    data-whiteboard-toggle  — freeze the current diagram and enable the
 *                              whiteboard engine on top of it.
 *
 *  Focus mode shows the LIVE Plotly chart (moved into the overlay), so
 *  it looks pixel-identical to the module page and hover tooltips work.
 *  Freeze & draw takes a PNG snapshot for a stable drawing surface.
 *
 *  The overlay is rendered by templates/partials/_module_body.html
 *  (look for data-focus-overlay). It is hidden by default; we toggle
 *  the [hidden] attribute to show / hide it.
 */
(function () {
  "use strict";

  // ─── helpers ───────────────────────────────────────────────
  function getPlotlyDiv() {
    const page = document.querySelector("[data-module-page]");
    const module = (page && page.dataset && page.dataset.module) || "";
    return document.getElementById("plot-" + module);
  }

  function freezeCurrentDiagram() {
    return new Promise(function (resolve) {
      const gd = getPlotlyDiv();
      const overlay = document.querySelector("[data-focus-overlay]");
      if (!overlay) { resolve(null); return; }
      const img = overlay.querySelector("[data-focus-backdrop]");
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
          }
          resolve(dataUrl);
        })
        .catch(function () {
          if (img) img.hidden = true;
          resolve(null);
        });
    });
  }

  // ─── live‑chart move tracking ────────────────────────────
  let plotlyOriginInfo = null;

  function movePlotlyIntoOverlay(overlay) {
    const gd = getPlotlyDiv();
    if (!gd || overlay.contains(gd)) return;
    const stage = overlay.querySelector(".focus-stage");
    if (!stage) return;
    plotlyOriginInfo = {
      parent: gd.parentElement,
      next: gd.nextElementSibling,
    };
    // Insert *before* the backdrop img so the backdrop (when visible)
    // renders on top at the same z-index.
    const img = overlay.querySelector("[data-focus-backdrop]");
    if (img && img.parentElement === stage) {
      stage.insertBefore(gd, img);
    } else {
      stage.appendChild(gd);
    }
  }

  function movePlotlyBack() {
    const gd = getPlotlyDiv();
    if (!gd || !plotlyOriginInfo) return;
    const { parent, next } = plotlyOriginInfo;
    if (parent) {
      if (next && next.parentElement === parent) {
        parent.insertBefore(gd, next);
      } else {
        parent.appendChild(gd);
      }
    }
    plotlyOriginInfo = null;
  }

  function openOverlay() {
    const overlay = document.querySelector("[data-focus-overlay]");
    if (!overlay) return;
    overlay.hidden = false;
    document.body.classList.add("focus-open");
    // Move the live Plotly chart into the overlay so it renders
    // inside the full‑screen view (no frozen snapshot needed).
    movePlotlyIntoOverlay(overlay);
    if (overlay.requestFullscreen) {
      overlay.requestFullscreen().catch(function () { /* ignored */ });
    }
  }

  function closeOverlay() {
    const overlay = document.querySelector("[data-focus-overlay]");
    if (!overlay) return;
    overlay.hidden = true;
    document.body.classList.remove("focus-open");
    // Restore the Plotly chart to its original container.
    movePlotlyBack();
    if (document.fullscreenElement === overlay && document.exitFullscreen) {
      document.exitFullscreen().catch(function () { /* ignored */ });
    }
  }

  function isOverlayOpen() {
    const overlay = document.querySelector("[data-focus-overlay]");
    return !!(overlay && !overlay.hidden);
  }

  // ─── handlers ──────────────────────────────────────────────
  function onFocusToggle(evt) {
    if (evt) evt.preventDefault();
    if (isOverlayOpen()) {
      closeOverlay();
    } else {
      // Focus mode: open the overlay and show the live chart.
      // Hide the canvas + tools since this is view‑only.
      openOverlay();
      const overlay = document.querySelector("[data-focus-overlay]");
      if (overlay) {
        const canvas = overlay.querySelector("[data-focus-canvas-wrap], .focus-canvas-wrap");
        if (canvas) canvas.style.display = "none";
        const toolbar = overlay.querySelector(".focus-toolbar");
        if (toolbar) toolbar.style.display = "none";
      }
    }
  }

  function onWhiteboardToggle(evt) {
    if (evt) evt.preventDefault();
    const overlay = document.querySelector("[data-focus-overlay]");
    if (!overlay) return;
    const canvasWrap = overlay.querySelector("[data-wb-canvas-wrap]");
    const toolbar = overlay.querySelector(".focus-toolbar");
    if (canvasWrap) canvasWrap.style.display = "";
    if (toolbar) toolbar.style.display = "";

    const wasOpen = isOverlayOpen();
    // Freeze the current diagram so the drawing surface is stable.
    freezeCurrentDiagram().then(function () {
      if (!wasOpen) openOverlay();
      requestAnimationFrame(function () {
        if (window.Whiteboard && typeof Whiteboard.init === "function") {
          Whiteboard.init({ wrap: canvasWrap });
          if (typeof Whiteboard.refresh === "function") Whiteboard.refresh();
        }
      });
    });
  }

  function onKeydown(evt) {
    if (!isOverlayOpen()) return;
    if (evt.key === "Escape") {
      evt.preventDefault();
      closeOverlay();
    }
  }

  // ─── bind once on load ─────────────────────────────────────
  function bind() {
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
    document.addEventListener("keydown", onKeydown);
    // Pull the formula + title into the overlay for context.
    const page = document.querySelector("[data-module-page]");
    const overlay = document.querySelector("[data-focus-overlay]");
    if (page && overlay) {
      const f = overlay.querySelector("[data-focus-formula]");
      if (f && page.dataset.formula) f.textContent = page.dataset.formula;
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", bind);
  } else {
    bind();
  }
})();
