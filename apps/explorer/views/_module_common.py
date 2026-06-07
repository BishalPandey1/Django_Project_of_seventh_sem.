"""Shared helpers for explorer module views."""

import json
import math

from django.shortcuts import render
from django.http import HttpResponseForbidden

from apps.accounts.models import ALL_MODULES, get_or_create_profile
from apps.explorer.mathlib import build_plot, get_module
from apps.explorer.mathlib.geometry import SHAPE_DEFAULTS, SHAPES
from apps.explorer.forms import FORM_MAP


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
    """Return a dict of clean params (or defaults on invalid)."""
    if form.is_valid():
        params = {k: form.cleaned_data[k] for k in allowed}
    else:
        params = {k: form.fields[k].initial for k in allowed}
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
}


def _render_module_inputs(request, module, params):
    """Render the inputs grid of a per-module template as an HTML string.

    Uses a dedicated ``_module_inputs.html`` fragment (no extends) so the
    result is a self-contained grid of input cards. The full page and the
    HTMX body partial both include this same fragment, so the inputs stay
    in sync when a slider is dragged.
    """
    from django.template.loader import render_to_string
    from apps.explorer.forms import FORM_MAP
    from apps.explorer.mathlib.transform import PRESETS
    form_cls, _ = FORM_MAP[module]
    form = form_cls(initial=params)
    ctx = {
        "module": module,
        "params": params,
        "form": form,
        "presets": PRESETS if module == "transform" else [],
    }
    inner = render_to_string(
        f"explorer/modules/_{module}_inputs.html", ctx, request=request,
    )
    return (
        '<section class="board-section" data-board="input">'
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
          '</div>'
        '</header>'
        '<div class="board-body">'
          '<div class="grid grid-cols-1 gap-3 sm:grid-cols-2" data-input-grid>'
            + inner +
          '</div>'
        '</div>'
        '</section>'
    )


def _module_view(request, module, template_name):
    if not _module_access(request.user, module):
        return HttpResponseForbidden("You do not have access to this module.")
    form, allowed = _build_module_form(module, request)
    params = _form_data_to_params(form, allowed, module)
    mathlib = get_module(module)
    try:
        if module == "geometry":
            shape = params.get("shape", "circle")
            computed = mathlib.compute(shape, **{k: v for k, v in params.items() if k != "shape"})
        else:
            computed = mathlib.compute(**{k: v for k, v in params.items() if k in allowed})
        if module == "geometry":
            steps = mathlib.steps(shape, **{k: v for k, v in computed.items() if k != "shape"})
        else:
            steps = mathlib.steps(**{**params, **computed})
    except (ValueError, ZeroDivisionError, OverflowError):
        computed = {}
        steps = []
    solvers = mathlib.solvers() if hasattr(mathlib, "solvers") else {"vars": [], "solvers": {}}
    plot = build_plot(module, {**params, **computed})
    plot_json = json.dumps(plot)
    insights = _build_insights(module, params, computed)
    inputs_html = _render_module_inputs(request, module, params)
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
        "is_htmx": request.headers.get("HX-Request") == "true",
        "inputs_html": inputs_html,
    }
    if ctx["is_htmx"]:
        return render(request, "partials/_module_body.html", ctx)
    return render(request, f"explorer/modules/{template_name}.html", ctx)


def _build_insights(module, params, c):
    """Return a list of stat dicts for the insight card."""
    items = []
    if module == "linear":
        xi = c['x_intercept']
        xi_str = "∞" if math.isnan(xi) else f"{xi:.3f}"
        items = [
            {"label": "Slope m",      "value": f"{c['slope']:.3f}",       "accent": "#3b82f6"},
            {"label": "Y-intercept",  "value": f"{c['y_intercept']:.3f}", "accent": "#f59e0b"},
            {"label": "X-intercept",  "value": xi_str,                     "accent": "#06b6d4"},
            {"label": "Angle θ",      "value": f"{c['angle_deg']:.2f}°",  "accent": "#a855f7"},
        ]
    elif module == "quadratic":
        items = [
            {"label": "Vertex x",     "value": f"{c['vertex_x']:.3f}",    "accent": "#3b82f6"},
            {"label": "Vertex y",     "value": f"{c['vertex_y']:.3f}",    "accent": "#a855f7"},
            {"label": "Discriminant", "value": f"{c['disc']:.3f}",        "accent": "#f97316"},
            {"label": "Opens",        "value": c["opens"],                "accent": "#10b981"},
            {"label": "Roots",        "value": c["nature"],               "accent": "#06b6d4"},
        ]
    elif module == "trig":
        items = [
            {"label": "Amplitude",    "value": f"{c['amplitude']:.3f}",   "accent": "#3b82f6"},
            {"label": "Period",       "value": f"{c['period']:.3f}",      "accent": "#a855f7"},
            {"label": "Phase shift",  "value": f"{c['phase_shift']:.3f}", "accent": "#f59e0b"},
            {"label": "Midline",      "value": f"{c['midline']:.3f}",     "accent": "#10b981"},
        ]
    elif module == "derivative":
        items = [
            {"label": "y₀ = f(x₀)",   "value": f"{c['y0']:.3f}",          "accent": "#3b82f6"},
            {"label": "Secant slope", "value": f"{c['slope_secant']:.4f}", "accent": "#a855f7"},
            {"label": "Exact slope",  "value": f"{c['slope_exact']:.4f}",  "accent": "#f97316"},
            {"label": "Error",        "value": f"{c['error']:.2e}",        "accent": "#ef4444"},
        ]
    elif module == "integral":
        items = [
            {"label": "Δx",           "value": f"{c['dx']:.4f}",          "accent": "#3b82f6"},
            {"label": "Riemann",      "value": f"{c['riemann']:.4f}",      "accent": "#a855f7"},
            {"label": "Exact",        "value": f"{c['exact']:.4f}",        "accent": "#10b981"},
            {"label": "Error",        "value": f"{c['error']:.4f}",        "accent": "#ef4444"},
        ]
    elif module == "geometry":
        s = c["shape"]
        items = [{"label": "Shape", "value": s, "accent": "#3b82f6"}]
        for k, v in c.items():
            if k in {"shape", "vertices"}:
                continue
            if isinstance(v, (int, float)):
                items.append({"label": k, "value": f"{v:.3f}", "accent": "#a855f7"})
    elif module == "transform":
        items = [
            {"label": "det(M)",        "value": f"{c['det']:.4f}",   "accent": "#3b82f6"},
            {"label": "M·î",           "value": f"({c['i_hat'][0]:.2f}, {c['i_hat'][1]:.2f})", "accent": "#10b981"},
            {"label": "M·ĵ",           "value": f"({c['j_hat'][0]:.2f}, {c['j_hat'][1]:.2f})", "accent": "#06b6d4"},
            {"label": "Orientation",   "value": c["orientation"],    "accent": "#a855f7"},
            {"label": "Singular",      "value": "yes" if c["singular"] else "no", "accent": "#ef4444"},
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
            computed = mathlib.compute(shape, **{k: v for k, v in params.items() if k != "shape"})
        else:
            computed = mathlib.compute(**{k: v for k, v in params.items() if k in allowed})
        if module == "geometry":
            steps = mathlib.steps(shape, **{k: v for k, v in computed.items() if k != "shape"})
        else:
            steps = mathlib.steps(**{**params, **computed})
    except (ValueError, ZeroDivisionError, OverflowError):
        computed = {}
        steps = []
    solvers = mathlib.solvers() if hasattr(mathlib, "solvers") else {"vars": [], "solvers": {}}
    plot = build_plot(module, {**params, **computed})
    plot_json = json.dumps(plot)
    insights = _build_insights(module, params, computed)
    inputs_html = _render_module_inputs(request, module, params)
    return render(request, "partials/_module_body.html", {
        "module": module,
        "module_description": DESCRIPTIONS.get(module, ""),
        "form": form, "params": params, "computed": computed,
        "plot_json": plot_json, "insights": insights, "steps": steps, "solvers": solvers,
        "inputs_html": inputs_html,
        "is_htmx": True,
    })
