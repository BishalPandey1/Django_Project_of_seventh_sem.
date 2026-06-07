"""Shared helpers for explorer module views."""

import json
import math

from django.shortcuts import render
from django.http import HttpResponseForbidden

from apps.accounts.models import ALL_MODULES, get_or_create_profile
from apps.explorer.mathlib import build_plot, get_module
from apps.explorer.mathlib.geometry import SHAPE_DEFAULTS, SHAPES
from apps.explorer.forms import FORM_MAP
from apps.explorer.mathlib import (
    linear as linear_ml,
    quadratic as quadratic_ml,
    trig as trig_ml,
    derivative as derivative_ml,
    integral as integral_ml,
    geometry as geometry_ml,
    transform as transform_ml,
    statistics as statistics_ml,
)
from apps.explorer.mathlib.geometry import SHAPE_PARAMS as GEO_PARAMS


def _coerce_params(module, raw_params):
    """Cast/clean params before calling mathlib.compute()."""
    if module == "integral":
        if raw_params.get("a", 0) >= raw_params.get("b", 0):
            raw_params["a"], raw_params["b"] = 0.0, max(1.0, float(raw_params.get("b", 1)))
    if module == "geometry":
        shape = raw_params.get("shape") or "circle"
        if shape not in SHAPES:
            shape = "circle"
        raw_params["shape"] = shape
        for k, v in SHAPE_DEFAULTS[shape].items():
            raw_params.setdefault(k, v)
    return raw_params


def _get_request_param(request, key, default=None):
    v = request.GET.get(key)
    if v is None:
        v = request.POST.get(key)
    if v is None or v == "":
        return default
    return v


def _build_module_form(module, request):
    form_cls, allowed = FORM_MAP[module]
    if request.method == "POST" and "__reset" not in request.POST:
        form = form_cls(request.POST)
    else:
        form = form_cls()
    return form, allowed


def _form_data_to_params(form, allowed, module):
    """Return a dict of clean params (or full defaults on invalid).

    With the new form contract every field is ``required=False`` and a
    module-level ``clean()`` fills in defaults for missing keys, so a
    single-slider POST still produces a complete ``cleaned_data``. We
    therefore read every key the form knows about (so the user's input
    for *every* slider, not just the ones in ``allowed``, reaches the
    mathlib) and fall back to all field defaults if the form is invalid.
    """
    if form.is_valid():
        params = {k: v for k, v in form.cleaned_data.items() if v is not None}
    else:
        params = {
            name: field.initial
            for name, field in form.fields.items()
            if field.initial is not None
        }
    return _coerce_params(module, params)


def _module_access(user, module):
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    profile = get_or_create_profile(user)
    return module in (profile.allowed_modules or []) or profile.role == "admin"


DESCRIPTIONS = {
    "linear":     "Plot y = m·x + b, see intercepts and the angle of the line.",
    "quadratic":  "Plot a·x² + b·x + c, find the vertex, discriminant and roots.",
    "trig":       "Plot A·sin(B·x + C) + D, see amplitude, period and phase shift.",
    "derivative": "Estimate the derivative of f at x₀ with the secant line, then compare to the exact value.",
    "integral":   "Approximate ∫ₐᵇ f(x) dx with left, right, midpoint or trapezoid Riemann sums.",
    "geometry":   "Pick a shape, tweak its parameters, see area, perimeter and the rendered figure.",
    "transform":  "Apply a 2×2 matrix M = [a b; c d] to the standard basis and see where the unit square goes.",
    "statistics": "Explore the normal distribution: adjust μ and σ, see the histogram, PDF, and summary statistics.",
}


PRESETS_BY_MODULE = {
    "linear":     linear_ml.PRESETS,
    "quadratic":  quadratic_ml.PRESETS,
    "trig":       trig_ml.PRESETS,
    "derivative": derivative_ml.PRESETS,
    "integral":   integral_ml.PRESETS,
    "geometry":   geometry_ml.PRESETS,
    "transform":  transform_ml.PRESETS,
    "statistics": statistics_ml.PRESETS,
}
BOUNDS_BY_MODULE = {
    "linear":     linear_ml.BOUNDS,
    "quadratic":  quadratic_ml.BOUNDS,
    "trig":       trig_ml.BOUNDS,
    "derivative": derivative_ml.BOUNDS,
    "integral":   integral_ml.BOUNDS,
    "geometry":   geometry_ml.BOUNDS,
    "transform":  transform_ml.BOUNDS,
    "statistics": statistics_ml.BOUNDS,
}
FORMULA_BY_MODULE = {
    "linear":     linear_ml.FORMULA,
    "quadratic":  quadratic_ml.FORMULA,
    "trig":       trig_ml.FORMULA,
    "derivative": derivative_ml.FORMULA,
    "integral":   integral_ml.FORMULA,
    "geometry":   geometry_ml.FORMULA,
    "transform":  transform_ml.FORMULA,
    "statistics": statistics_ml.FORMULA,
}


def _formula_string(module, params, computed):
    """Build a short, human-readable formula string for the current state."""
    fn = FORMULA_BY_MODULE.get(module)
    if fn is None:
        return ""
    try:
        merged = {k: v for k, v in params.items() if v is not None}
        if computed:
            for k, v in computed.items():
                if k in merged and merged[k] != v and isinstance(v, (int, float)):
                    merged[k] = v
        return fn(**merged)
    except Exception:
        return ""


def _render_module_inputs(request, module, params):
    """Render the inputs grid of a per-module template as an HTML string.

    Uses a dedicated ``_module_inputs.html`` fragment (no extends) so the
    result is a self-contained grid of input cards. The full page and the
    HTMX body partial both include this same fragment, so the inputs stay
    in sync when a slider is dragged.
    """
    from django.template.loader import render_to_string
    form_cls, _ = FORM_MAP[module]
    form = form_cls(initial=params)
    raw_presets = PRESETS_BY_MODULE.get(module, [])
    # Pre-serialize each preset's params so the template can hand a clean
    # JSON object to ``hx-vals`` without any custom filter.
    presets = []
    for p in raw_presets:
        presets.append({
            "name":  p.get("name", ""),
            "blurb": p.get("blurb", ""),
            "params_json": json.dumps(p.get("params", {})),
        })
    ctx = {
        "module": module,
        "params": params,
        "form": form,
        "presets": presets,
        "bounds": BOUNDS_BY_MODULE.get(module, {}),
    }
    inner = render_to_string(
        f"explorer/modules/_{module}_inputs.html", ctx, request=request,
    )
    return (
        '<section class="board-section" data-board="input" data-input-board>'
        '<header class="board-header">'
          '<div class="board-title">'
            '<span class="board-title-badge">1</span>'
            '<div class="board-title-text">'
              '<span class="board-title-eyebrow">Step 1</span>'
              '<span class="board-title-h">Input — put your values</span>'
            '</div>'
          '</div>'
          '<div class="board-actions">'
            '<button type="button" data-reset-module class="btn btn-secondary">'
              '<svg class="h-3.5 w-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
                'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
                '<path d="M3 12a9 9 0 1 0 3-6.7L3 8"/><path d="M3 3v5h5"/>'
              '</svg>'
              'Reset'
            '</button>'
            '<button type="button" data-snapshot-button class="btn btn-secondary" '
                    'title="Freeze the current curve and overlay it on the diagram">'
              '<svg class="h-3.5 w-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
                'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
                '<rect x="3" y="6" width="18" height="13" rx="2"/>'
                '<circle cx="12" cy="12.5" r="3.5"/>'
                '<path d="M7 6V4h10v2"/>'
              '</svg>'
              'Snapshot'
            '</button>'
          '</div>'
        '</header>'
        '<div class="board-body">'
          '<div class="grid grid-cols-1 gap-3 sm:grid-cols-2" data-input-grid>'
            + inner +
          '</div>'
        '</div>'
        '</section>'
    )


def _snapshot_key(module):
    return f"explorer_snapshot_{module}"


def _build_plot_with_snapshot(module, current_params, computed, request):
    """Build the plot for the current params, overlaying a frozen snapshot
    from the session if one exists.

    Snapshot data is stored as plain JSON-safe dicts (no callables) so
    it round-trips through the session.
    """
    plot = build_plot(module, {**current_params, **computed})
    snap_raw = request.session.get(_snapshot_key(module)) if hasattr(request, "session") else None
    if not snap_raw:
        return plot, None
    snap_params = snap_raw.get("params") or {}
    snap_label  = snap_raw.get("label") or "previous"
    try:
        if module == "geometry":
            shape = snap_params.get("shape", "circle")
            shape_keys = [p[0] for p in GEO_PARAMS.get(shape, [])]
            shape_kwargs = {k: v for k, v in snap_params.items() if k in shape_keys}
            from apps.explorer.mathlib.geometry import compute as _geo_compute
            snap_computed = _geo_compute(shape, **shape_kwargs)
        else:
            mathlib = get_module(module)
            snap_computed = mathlib.compute(**{k: v for k, v in snap_params.items() if k in FORM_MAP[module][1]})
        snap_plot = build_plot(module, {**snap_params, **snap_computed})
    except Exception:
        return plot, None
    # Tag every snapshot trace and apply a faded style so the user can
    # tell the snapshot from the live curve.
    for trace in snap_plot.get("data", []):
        trace["name"] = "snapshot"
        line = trace.get("line") or {}
        line["dash"]  = "dot"
        line["width"] = 2
        line["color"] = "#94a3b8"
        trace["line"] = line
        trace["opacity"] = 0.55
        trace["hoverinfo"] = "skip"
    plot["data"] = list(plot.get("data", [])) + list(snap_plot.get("data", []))
    return plot, {"label": snap_label, "params": snap_params}


def _module_view(request, module, template_name):
    if not _module_access(request.user, module):
        return HttpResponseForbidden("You do not have access to this module.")
    form, allowed = _build_module_form(module, request)
    params = _form_data_to_params(form, allowed, module)
    mathlib = get_module(module)
    try:
        if module == "geometry":
            shape = params.get("shape", "circle")
            shape_keys = [p[0] for p in GEO_PARAMS.get(shape, [])]
            shape_kwargs = {k: v for k, v in params.items() if k in shape_keys}
            computed = mathlib.compute(shape, **shape_kwargs)
        else:
            computed = mathlib.compute(**{k: v for k, v in params.items() if k in allowed})
        if module == "geometry":
            shape_keys = [p[0] for p in GEO_PARAMS.get(shape, [])]
            steps_kwargs = {k: v for k, v in {**params, **computed}.items()
                            if k in shape_keys}
            steps = mathlib.steps(shape, **steps_kwargs)
        else:
            steps = mathlib.steps(**{**params, **computed})
    except (ValueError, ZeroDivisionError, OverflowError, TypeError):
        computed = {}
        steps = []
    solvers = _module_solvers(mathlib, params)
    plot, snapshot = _build_plot_with_snapshot(module, params, computed, request)
    plot_json = json.dumps(plot)
    insights = _build_insights(module, params, computed)
    inputs_html = _render_module_inputs(request, module, params)
    formula = _formula_string(module, params, computed)
    ctx = {
        "module": module,
        "module_description": DESCRIPTIONS.get(module, ""),
        "form": form,
        "params": params,
        "computed": computed,
        "plot_json": plot_json,
        "insights": insights,
        "steps": steps,
        "solvers": solvers,
        "snapshot": snapshot,
        "is_htmx": request.headers.get("HX-Request") == "true",
        "inputs_html": inputs_html,
        "formula": formula,
        "bounds": BOUNDS_BY_MODULE.get(module, {}),
    }
    if ctx["is_htmx"]:
        return render(request, "partials/_module_body.html", ctx)
    return render(request, f"explorer/modules/{template_name}.html", ctx)


def _build_insights(module, params, c):
    """Return a list of stat dicts for the insight card.

    Each dict MAY carry ``bind_to`` (input name) and ``bind_value`` (current
    numeric value). When present, the insight card is click-to-edit and
    pushes the new value back to that input via HTMX.
    """
    items = []
    if module == "linear":
        xi = c['x_intercept']
        xi_str = "∞" if math.isnan(xi) else f"{xi:.3f}"
        items = [
            {"label": "Slope m",      "value": f"{c['slope']:.3f}",       "accent": "#3b82f6",
             "bind_to": "m", "bind_value": float(c['slope'])},
            {"label": "Y-intercept",  "value": f"{c['y_intercept']:.3f}", "accent": "#f59e0b",
             "bind_to": "b", "bind_value": float(c['y_intercept'])},
            {"label": "X-intercept",  "value": xi_str,                     "accent": "#06b6d4",
             "bind_to": "m", "bind_value": float(c['slope'])},
            {"label": "Angle θ",      "value": f"{c['angle_deg']:.2f}°",  "accent": "#a855f7",
             "bind_to": "m", "bind_value": float(c['slope'])},
        ]
    elif module == "quadratic":
        items = [
            {"label": "Vertex x",     "value": f"{c['vertex_x']:.3f}",    "accent": "#3b82f6",
             "bind_to": "a", "bind_value": float(c['a'])},
            {"label": "Vertex y",     "value": f"{c['vertex_y']:.3f}",    "accent": "#a855f7",
             "bind_to": "c", "bind_value": float(c['c'])},
            {"label": "Discriminant", "value": f"{c['disc']:.3f}",        "accent": "#f97316",
             "bind_to": "c", "bind_value": float(c['c'])},
            {"label": "Opens",        "value": c["opens"],                "accent": "#10b981",
             "bind_to": "a", "bind_value": float(c['a'])},
            {"label": "Roots",        "value": c["nature"],               "accent": "#06b6d4",
             "bind_to": "a", "bind_value": float(c['a'])},
        ]
    elif module == "trig":
        items = [
            {"label": "Amplitude",    "value": f"{c['amplitude']:.3f}",   "accent": "#3b82f6",
             "bind_to": "A", "bind_value": float(c['A'])},
            {"label": "Period",       "value": f"{c['period']:.3f}",      "accent": "#a855f7",
             "bind_to": "B", "bind_value": float(c['B'])},
            {"label": "Phase shift",  "value": f"{c['phase_shift']:.3f}", "accent": "#f59e0b",
             "bind_to": "C", "bind_value": float(c['C'])},
            {"label": "Midline",      "value": f"{c['midline']:.3f}",     "accent": "#10b981",
             "bind_to": "D", "bind_value": float(c['D'])},
        ]
    elif module == "derivative":
        items = [
            {"label": "y₀ = f(x₀)",   "value": f"{c['y0']:.3f}",          "accent": "#3b82f6",
             "bind_to": "x0", "bind_value": float(c['x0'])},
            {"label": "Secant slope", "value": f"{c['slope_secant']:.4f}", "accent": "#a855f7",
             "bind_to": "h",  "bind_value": float(c['h'])},
            {"label": "Exact slope",  "value": f"{c['slope_exact']:.4f}",  "accent": "#f97316",
             "bind_to": "h",  "bind_value": float(c['h'])},
            {"label": "Error",        "value": f"{c['error']:.2e}",        "accent": "#ef4444",
             "bind_to": "h",  "bind_value": float(c['h'])},
        ]
    elif module == "integral":
        items = [
            {"label": "Δx",           "value": f"{c['dx']:.4f}",          "accent": "#3b82f6",
             "bind_to": "n", "bind_value": float(c['n'])},
            {"label": "Riemann",      "value": f"{c['riemann']:.4f}",      "accent": "#a855f7",
             "bind_to": "n", "bind_value": float(c['n'])},
            {"label": "Exact",        "value": f"{c['exact']:.4f}",        "accent": "#10b981",
             "bind_to": "b", "bind_value": float(c['b'])},
            {"label": "Error",        "value": f"{c['error']:.4f}",        "accent": "#ef4444",
             "bind_to": "n", "bind_value": float(c['n'])},
        ]
    elif module == "geometry":
        s = c["shape"]
        items = [{"label": "Shape", "value": s, "accent": "#3b82f6"}]
        for k, v in c.items():
            if k in {"shape", "vertices"}:
                continue
            if isinstance(v, (int, float)):
                items.append({
                    "label": k,
                    "value": f"{v:.3f}",
                    "accent": "#a855f7",
                    "bind_to": k if k in params else None,
                    "bind_value": float(v) if k in params else None,
                })
    elif module == "transform":
        items = [
            {"label": "det(M)",        "value": f"{c['det']:.4f}",   "accent": "#3b82f6",
             "bind_to": "a", "bind_value": float(c['a'])},
            {"label": "M·î",           "value": f"({c['i_hat'][0]:.2f}, {c['i_hat'][1]:.2f})",
             "accent": "#10b981", "bind_to": "a", "bind_value": float(c['a'])},
            {"label": "M·ĵ",           "value": f"({c['j_hat'][0]:.2f}, {c['j_hat'][1]:.2f})",
             "accent": "#06b6d4", "bind_to": "d", "bind_value": float(c['d'])},
            {"label": "Trace",         "value": f"{c['trace']:.3f}",  "accent": "#f97316",
             "bind_to": "a", "bind_value": float(c['a'])},
            {"label": "Orientation",   "value": c["orientation"],    "accent": "#a855f7"},
            {"label": "Singular",      "value": "yes" if c["singular"] else "no", "accent": "#ef4444"},
        ]
    elif module == "statistics":
        items = [
            {"label": "Sample mean",   "value": f"{c['sample_mean']:.3f}", "accent": "#3b82f6",
             "bind_to": "mean", "bind_value": float(c['mean'])},
            {"label": "Std dev",       "value": f"{c['sample_std']:.3f}", "accent": "#a855f7",
             "bind_to": "stddev", "bind_value": float(c['stddev'])},
            {"label": "Variance",      "value": f"{c['variance']:.3f}", "accent": "#f97316"},
            {"label": "Median",        "value": f"{c['median']:.3f}", "accent": "#10b981",
             "bind_to": "mean", "bind_value": float(c['mean'])},
            {"label": "Q₁",            "value": f"{c['q1']:.3f}", "accent": "#06b6d4"},
            {"label": "Q₃",            "value": f"{c['q3']:.3f}", "accent": "#ec4899"},
            {"label": "IQR",           "value": f"{c['iqr']:.3f}", "accent": "#f59e0b"},
            {"label": "Within 1σ",     "value": f"{c['pct_1sigma']:.1f}%", "accent": "#3b82f6"},
            {"label": "Within 2σ",     "value": f"{c['pct_2sigma']:.1f}%", "accent": "#a855f7"},
        ]
    return items


def _module_update(request, module):
    """HTMX POST endpoint for a module — returns just the #module-body fragment."""
    if not _module_access(request.user, module):
        return HttpResponseForbidden("You do not have access to this module.")
    form, allowed = _build_module_form(module, request)
    params = _form_data_to_params(form, allowed, module)
    mathlib = get_module(module)
    try:
        if module == "geometry":
            shape = params.get("shape", "circle")
            shape_keys = [p[0] for p in GEO_PARAMS.get(shape, [])]
            shape_kwargs = {k: v for k, v in params.items() if k in shape_keys}
            computed = mathlib.compute(shape, **shape_kwargs)
        else:
            computed = mathlib.compute(**{k: v for k, v in params.items() if k in allowed})
        if module == "geometry":
            shape_keys = [p[0] for p in GEO_PARAMS.get(shape, [])]
            steps_kwargs = {k: v for k, v in {**params, **computed}.items()
                            if k in shape_keys}
            steps = mathlib.steps(shape, **steps_kwargs)
        else:
            steps = mathlib.steps(**{**params, **computed})
    except (ValueError, ZeroDivisionError, OverflowError, TypeError):
        computed = {}
        steps = []
    solvers = _module_solvers(mathlib, params)
    plot, snapshot = _build_plot_with_snapshot(module, params, computed, request)
    plot_json = json.dumps(plot)
    insights = _build_insights(module, params, computed)
    inputs_html = _render_module_inputs(request, module, params)
    formula = _formula_string(module, params, computed)
    return render(request, "partials/_module_body.html", {
        "module": module,
        "module_description": DESCRIPTIONS.get(module, ""),
        "form": form, "params": params, "computed": computed,
        "plot_json": plot_json, "insights": insights, "steps": steps, "solvers": solvers,
        "inputs_html": inputs_html, "formula": formula,
        "bounds": BOUNDS_BY_MODULE.get(module, {}),
        "snapshot": snapshot, "is_htmx": True,
    })


def _module_snapshot(request, module):
    """HTMX POST — set or clear the frozen snapshot for this module.

    The body must include a ``__snapshot`` value of ``"set"`` or
    ``"clear"``; the rest of the form is the current parameter set.
    """
    if not _module_access(request.user, module):
        return HttpResponseForbidden("You do not have access to this module.")
    form, allowed = _build_module_form(module, request)
    params = _form_data_to_params(form, allowed, module)
    key = _snapshot_key(module)
    op = request.POST.get("__snapshot", "set")
    if op == "clear":
        request.session.pop(key, None)
    else:
        # Strip non-JSON-safe entries (callables, etc.) — params are
        # already scalars after _form_data_to_params.
        clean = {k: v for k, v in params.items() if isinstance(v, (int, float, str))}
        # Build a short label from a few key params.
        label = _formula_string(module, params, {}) or "previous"
        request.session[key] = {"params": clean, "label": label}
    return _module_update(request, module)


def _module_solvers(mathlib, params):
    """Return a solvers dict for the module, calling solvers(params) if it accepts them.

    Some modules (derivative, integral, geometry) make their solver formulas
    depend on the currently selected function / method / shape. They expose
    a ``solvers(params)`` signature; the rest still use ``solvers()``. This
    wrapper calls whichever signature is available.
    """
    import inspect
    if not hasattr(mathlib, "solvers"):
        return {"vars": [], "solvers": {}}
    try:
        sig = inspect.signature(mathlib.solvers)
    except (TypeError, ValueError):
        return mathlib.solvers()
    if len(sig.parameters) == 0:
        return mathlib.solvers()
    try:
        return mathlib.solvers(params)
    except Exception:
        return mathlib.solvers()
