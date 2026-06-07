/* Module Focus + Freeze & draw
 * ─────────────────────────────
 *  Two diagram-toolbar actions:
 *    data-focus-toggle       — open / close full-screen focus overlay
 *    data-whiteboard-toggle  — freeze the current diagram and enable the
 *                              whiteboard engine on top of it.
 *
 *  Focus mode takes a full-resolution PNG of the current Plotly chart
 *  (via Plotly.toImage) and displays it as the backdrop inside the
 *  full-screen overlay.  The frozen image exactly fills the 16:9 paper
 *  area so it looks pixel-identical to the live chart.
 *
 *  Freeze & draw works the same way but additionally shows the drawing
 *  canvas and toolbar on top of the frozen backdrop.
 *
 *  Re-binds the toolbar buttons after every HTMX swap so slider‑driven
 *  diagram updates never leave the buttons orphaned.
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
      // Capture at 1600×900 — matches the 16:9 paper area and stays
      // crisp on retina displays when upscaled to the display size.
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

  function openOverlay() {
    const overlay = document.querySelector("[data-focus-overlay]");
    if (!overlay) return;
    overlay.hidden = false;
    document.body.classList.add("focus-open");
    if (overlay.requestFullscreen) {
      overlay.requestFullscreen().catch(function () { /* ignored */ });
    }
  }

  function closeOverlay() {
    const overlay = document.querySelector("[data-focus-overlay]");
    if (!overlay) return;
    overlay.hidden = true;
    document.body.classList.remove("focus-open");
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
      // Focus mode: freeze the diagram, open the overlay, hide canvas
      // and toolbar (pure view‑only).
      freezeCurrentDiagram().then(function () {
        openOverlay();
        const overlay = document.querySelector("[data-focus-overlay]");
        if (overlay) {
          const canvas = overlay.querySelector("[data-focus-canvas-wrap], .focus-canvas-wrap");
          if (canvas) canvas.style.display = "none";
          const toolbar = overlay.querySelector(".focus-toolbar");
          if (toolbar) toolbar.style.display = "none";
        }
      });
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

  // ─── bind / re-bind ────────────────────────────────────────
  function reinit() {
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
    // Pull the formula + title into the overlay for context.
    const page = document.querySelector("[data-module-page]");
    const overlay = document.querySelector("[data-focus-overlay]");
    if (page && overlay) {
      const f = overlay.querySelector("[data-focus-formula]");
      if (f && page.dataset.formula) f.textContent = page.dataset.formula;
    }
  }

  function bind() {
    reinit();
    document.addEventListener("keydown", onKeydown);
    // Re-bind after every HTMX swap so slider‑driven updates never
    // orphan the Focus / Freeze‑&‑draw buttons.
    document.body.addEventListener("htmx:afterSwap", reinit);
    document.body.addEventListener("htmx:load",       reinit);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", bind);
  } else {
    bind();
  }
})();
