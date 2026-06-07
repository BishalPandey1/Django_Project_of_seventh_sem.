/* Module Focus + Freeze & draw
 * ─────────────────────────────
 *  Two new diagram-toolbar actions:
 *    data-focus-toggle  — open / close the full-screen focus overlay
 *    data-whiteboard-toggle — freeze the current diagram and enable the
 *                             same whiteboard engine the standalone
 *                             /board/ page uses, but pointed at the
 *                             /<module>/annotations/ endpoints.
 *
 *  The overlay is rendered by templates/partials/_module_body.html
 *  (look for data-focus-overlay). It is hidden by default; we toggle
 *  the [hidden] attribute to show / hide it.
 *
 *  State is intentionally local to this file (closure-scope) so we
 *  never collide with the rest of the module's JS.
 */
(function () {
  "use strict";

  // ─── helpers ───────────────────────────────────────────────
  function getPlotlyDiv() {
    // The Plotly graph div is created by plotly_init.js with id
    // `plot-<module>` inside the diagram board. We use the data-plot
    // attribute the partial also exposes for the coordinate readout.
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
      // 1600×900 keeps the diagram crisp on hi-DPI screens.
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
    // Try the browser's fullscreen API for true fullscreen; fall back
    // to a CSS-only overlay if it's denied (e.g. iframe context).
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
      // Just Focus mode: show the diagram as a frozen PNG. The user
      // can hit "Freeze & draw" inside the overlay to add annotations.
      freezeCurrentDiagram().then(function (dataUrl) {
        openOverlay();
        if (dataUrl) {
          const overlay = document.querySelector("[data-focus-overlay]");
          if (overlay) {
            // Hide the canvas + tools in pure-Focus mode.
            const canvas = overlay.querySelector("[data-focus-canvas-wrap], .focus-canvas-wrap");
            if (canvas) canvas.style.display = "none";
            const toolbar = overlay.querySelector(".focus-toolbar");
            if (toolbar) toolbar.style.display = "none";
          }
        }
      });
    }
  }

  function onWhiteboardToggle(evt) {
    if (evt) evt.preventDefault();
    // Always force-reopen with the whiteboard visible. If the overlay
    // is already open we just unhide the canvas + toolbar.
    const overlay = document.querySelector("[data-focus-overlay]");
    if (!overlay) return;
    const canvasWrap = overlay.querySelector("[data-wb-canvas-wrap]");
    const toolbar = overlay.querySelector(".focus-toolbar");
    if (canvasWrap) canvasWrap.style.display = "";
    if (toolbar) toolbar.style.display = "";

    // If we're already open, just refresh the engine so it picks up
    // the now-visible canvas dimensions. Otherwise open + freeze +
    // re-init.
    const wasOpen = isOverlayOpen();
    freezeCurrentDiagram().then(function () {
      if (!wasOpen) openOverlay();
      // Defer one frame so the canvas has a real bounding box.
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
    // All buttons with data-focus-toggle (toolbar + inside overlay).
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
