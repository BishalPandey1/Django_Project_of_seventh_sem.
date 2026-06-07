"""Build Plotly figure dicts for every explorer module.

Each builder returns ``{data, layout}`` ready for ``Plotly.react``.
The math modules call this once per state change and embed the
result in the page as JSON; client-side JS just hands it to Plotly.
"""

import math

# ── color constants matching the React chart palette ────────────────────
CHART = {1: "#3b82f6", 2: "#a855f7", 3: "#06b6d4", 4: "#f97316",
         5: "#10b981", 6: "#ec4899"}
ACCENT = "#f59e0b"
MUTED  = "#64748b"


# ── low-level helpers ───────────────────────────────────────────────────
def line_trace(xs, ys, color, width=3, dash=None, name=None):
    return {
        "type": "scatter",
        "mode": "lines",
        "x": list(xs), "y": list(ys),
        "line": {"color": color, "width": width, **({"dash": dash} if dash else {})},
        **({"name": name} if name else {}),
        "hoverinfo": "skip",
    }


def point_trace(x, y, color, label=None, size=8, symbol="circle"):
    return {
        "type": "scatter",
        "mode": "markers+text" if label else "markers",
        "x": [x], "y": [y],
        "marker": {"color": color, "size": size, "symbol": symbol, "line": {"color": "white", "width": 1}},
        "text": [label] if label else [],
        "textposition": "top center",
        "textfont": {"size": 11, "color": color},
        "showlegend": False,
    }


def fill_polygon_trace(points, fill_color, opacity=0.22):
    xs = [p[0] for p in points] + [points[0][0]]
    ys = [p[1] for p in points] + [points[0][1]]
    return {
        "type": "scatter", "mode": "lines",
        "x": xs, "y": ys, "fill": "toself",
        "fillcolor": fill_color.replace(")", f",{opacity})").replace("rgb", "rgba") if fill_color.startswith("rgb") else fill_color,
        "line": {"color": fill_color, "width": 2},
        "hoverinfo": "skip",
    }


def vline_shape(x, color, dashed=True):
    return {"type": "line", "x0": x, "x1": x, "y0": 0, "y1": 1,
            "xref": "x", "yref": "paper",
            "line": {"color": color, "width": 1, "dash": "dash" if dashed else "solid"}}


def hline_shape(y, color, dashed=True):
    return {"type": "line", "x0": 0, "x1": 1, "y0": y, "y1": y,
            "xref": "paper", "yref": "y",
            "line": {"color": color, "width": 1, "dash": "dash" if dashed else "solid"}}


def label_annotation(x, y, text, **kw):
    base = {"x": x, "y": y, "text": text, "showarrow": False,
            "font": {"size": 11, "color": MUTED}}
    base.update(kw)
    return base


def arc_shape(cx, cy, r, start_deg, end_deg, color, width=2):
    return {"type": "path",
            "path": _arc_path(cx, cy, r, start_deg, end_deg),
            "line": {"color": color, "width": width},
            "fillcolor": "rgba(0,0,0,0)"}


def right_angle_marker_shape(vx, ax, bx, color, size_px=14):
    """Return a list of two line-shapes forming a right-angle tick at vx."""
    # project ax, bx onto lines perpendicular/parallel to ab
    dx, dy = ax[0] - bx[0], ax[1] - bx[1]
    L = math.hypot(dx, dy) or 1
    ux, uy = dx / L, dy / L
    px, py = -uy, ux
    s = size_px
    p1 = (ax[0] + px * s, ax[1] + py * s)
    p2 = (p1[0] + ux * s, p1[1] + uy * s)
    return [
        {"type": "line", "x0": ax[0], "x1": p1[0], "y0": ax[1], "y1": p1[1],
         "line": {"color": color, "width": 1}},
        {"type": "line", "x0": p1[0], "x1": p2[0], "y0": p1[1], "y1": p2[1],
         "line": {"color": color, "width": 1}},
        {"type": "line", "x0": p2[0], "x1": bx[0], "y0": p2[1], "y1": bx[1],
         "line": {"color": color, "width": 1}},
    ]


def _arc_path(cx, cy, r, start_deg, end_deg):
    """SVG path for a circular arc (used in shape definitions)."""
    s = math.radians(start_deg)
    e = math.radians(end_deg)
    x0, y0 = cx + r * math.cos(s), cy + r * math.sin(s)
    x1, y1 = cx + r * math.cos(e), cy + r * math.sin(e)
    large = 1 if abs(end_deg - start_deg) > 180 else 0
    sweep = 1 if end_deg > start_deg else 0
    return f"M {x0:.3f} {y0:.3f} A {r:.3f} {r:.3f} 0 {large} {sweep} {x1:.3f} {y1:.3f}"


# ── auto-range helper ──────────────────────────────────────────────────
def _auto_range_xy(xs, ys, pad=0.15):
    if not xs or not ys:
        return (-10, 10, -10, 10)
    xmin, xmax = min(xs), max(xs)
    ymin, ymax = min(ys), max(ys)
    dx = (xmax - xmin) or 1
    dy = (ymax - ymin) or 1
    return (xmin - dx * pad, xmax + dx * pad,
            ymin - dy * pad, ymax + dy * pad)


def _linspace(a, b, n=400):
    if n < 2:
        return [a]
    step = (b - a) / (n - 1)
    return [a + i * step for i in range(n)]


# ── per-module builders ────────────────────────────────────────────────
def _linear(c):
    m, b = c["m"], c["b"]
    fn = c["fn"]
    xmin, xmax = -10, 10
    xs = _linspace(xmin, xmax, 400)
    ys = [fn(x) for x in xs]
    data = [line_trace(xs, ys, CHART[1], 3)]
    shapes = [
        vline_shape(0, MUTED), hline_shape(0, MUTED),
    ]
    annotations = []
    if not math.isnan(c["x_intercept"]):
        annotations.append(label_annotation(c["x_intercept"], 0, "x-int", yshift=-12))
        data.append(point_trace(c["x_intercept"], 0, CHART[2]))
    data.append(point_trace(0, c["y_intercept"], CHART[2]))
    annotations.append(label_annotation(0, c["y_intercept"], "y-int", xshift=14))
    return {
        "data": data,
        "layout": {
            "shapes": shapes,
            "annotations": annotations,
            "xaxis_range": [xmin, xmax],
            "yaxis_scaleanchor": "x", "yaxis_scaleratio": 1,
        },
    }


def _quadratic(c):
    fn = c["fn"]
    a, b, cc = c["a"], c["b"], c["c"]
    xmin, xmax = -10, 10
    xs = _linspace(xmin, xmax, 400)
    ys = [fn(x) for x in xs]
    data = [line_trace(xs, ys, CHART[2], 3)]
    annotations = [
        label_annotation(c["vertex_x"], c["vertex_y"], "vertex"),
    ]
    data.append(point_trace(c["vertex_x"], c["vertex_y"], CHART[4]))
    for r in c["roots"]:
        data.append(point_trace(r, 0, CHART[3]))
        annotations.append(label_annotation(r, 0, f"{r:.2f}", yshift=-12))
    return {
        "data": data,
        "layout": {
            "shapes": [vline_shape(0, MUTED), hline_shape(0, MUTED)],
            "annotations": annotations,
            "xaxis_range": [xmin, xmax],
            "yaxis_scaleanchor": "x", "yaxis_scaleratio": 1,
        },
    }


def _trig(c):
    fn = c["fn"]
    period = c["period"]
    if math.isinf(period) or period <= 0:
        period = 2 * math.pi
    xmin = c["phase_shift"] - 2 * period
    xmax = c["phase_shift"] + 2 * period
    xs = _linspace(xmin, xmax, 600)
    ys = [fn(x) for x in xs]
    data = [line_trace(xs, ys, CHART[3], 3)]
    shapes = [vline_shape(0, MUTED), hline_shape(c["midline"], MUTED, dashed=True)]
    annotations = [
        label_annotation(xmin + 0.2 * (xmax - xmin), c["midline"] + c["amplitude"],
                         f"A={c['amplitude']:.2f}", xanchor="left"),
    ]
    return {
        "data": data,
        "layout": {
            "shapes": shapes,
            "annotations": annotations,
            "xaxis_range": [xmin, xmax],
            "yaxis_scaleanchor": "x", "yaxis_scaleratio": 1,
        },
    }


def _derivative(c):
    fn = c["fn"]
    f_ex = c["tangent_fn"]
    f_sec = c["secant_fn"]
    x0 = c.get("x0", 0)
    xmin, xmax = x0 - 4, x0 + 4
    xs = _linspace(xmin, xmax, 400)
    ys = [fn(x) for x in xs]
    ts = [f_ex(x) for x in xs]
    ss = [f_sec(x) for x in xs]
    return {
        "data": [
            line_trace(xs, ys, CHART[4], 3),
            line_trace(xs, ts, CHART[1], 2, dash="dash"),
            line_trace(xs, ss, CHART[2], 2, dash="dot"),
            point_trace(x0, c["y0"], CHART[5], label="x₀"),
        ],
        "layout": {
            "shapes": [vline_shape(0, MUTED), hline_shape(0, MUTED)],
            "annotations": [],
            "xaxis_range": [xmin, xmax],
            "yaxis_scaleanchor": "x", "yaxis_scaleratio": 1,
        },
    }


def _integral(c):
    fn = c["fn"]
    a, b = c.get("a", 0), c.get("b", 1)
    if a == b:
        a, b = 0, 1
    span = b - a
    xmin = a - 0.4 * span
    xmax = b + 0.4 * span
    xs = _linspace(xmin, xmax, 400)
    ys = [fn(x) for x in xs]
    traces = [line_trace(xs, ys, CHART[1], 3)]
    # rectangles
    for bar in c.get("bars", []):
        x1, x2, y = bar["x1"], bar["x2"], bar["y"]
        traces.append({
            "type": "scatter", "mode": "lines",
            "x": [x1, x2, x2, x1, x1], "y": [0, 0, y, y, 0],
            "line": {"color": CHART[5], "width": 1},
            "fill": "toself", "fillcolor": "rgba(236,72,153,0.12)",
            "showlegend": False, "hoverinfo": "skip",
        })
    return {
        "data": traces,
        "layout": {
            "shapes": [vline_shape(0, MUTED), hline_shape(0, MUTED),
                       vline_shape(a, ACCENT, dashed=True), vline_shape(b, ACCENT, dashed=True)],
            "annotations": [
                label_annotation(a, 0, "a", yshift=-12),
                label_annotation(b, 0, "b", yshift=-12),
            ],
            "xaxis_range": [xmin, xmax],
            "yaxis_scaleanchor": "x", "yaxis_scaleratio": 1,
        },
    }


def _geometry(c):
    shape = c["shape"]
    annotations = []
    shapes = [vline_shape(0, MUTED), hline_shape(0, MUTED)]
    traces = []
    if shape == "circle":
        cx, cy, r = c["cx"], c["cy"], c["r"]
        theta = _linspace(0, 2 * math.pi, 120)
        traces.append(line_trace([cx + r * math.cos(t) for t in theta],
                                 [cy + r * math.sin(t) for t in theta],
                                 CHART[1], 3))
    elif shape == "ellipse":
        theta = _linspace(0, 2 * math.pi, 120)
        traces.append(line_trace([c["rx"] * math.cos(t) for t in theta],
                                 [c["ry"] * math.sin(t) for t in theta],
                                 CHART[1], 3))
    elif shape == "square":
        s = c["s"]
        pts = [(-s/2, -s/2), (s/2, -s/2), (s/2, s/2), (-s/2, s/2)]
        traces.append(line_trace([p[0] for p in pts + [pts[0]]],
                                 [p[1] for p in pts + [pts[0]]], CHART[1], 3))
    elif shape == "rectangle":
        L, W = c["L"], c["W"]
        pts = [(-L/2, -W/2), (L/2, -W/2), (L/2, W/2), (-L/2, W/2)]
        traces.append(line_trace([p[0] for p in pts + [pts[0]]],
                                 [p[1] for p in pts + [pts[0]]], CHART[1], 3))
    elif shape == "triangle":
        v = c["vertices"]
        traces.append(line_trace([p[0] for p in v + [v[0]]],
                                 [p[1] for p in v + [v[0]]], CHART[1], 3))
    elif shape == "rightTriangle":
        a, b = c["a"], c["b"]
        pts = [(0, 0), (a, 0), (0, b)]
        traces.append(line_trace([p[0] for p in pts + [pts[0]]],
                                 [p[1] for p in pts + [pts[0]]], CHART[1], 3))
        shapes.extend(right_angle_marker_shape((0, 0), (a, 0), (0, b), CHART[2]))
    elif shape == "parallelogram":
        base, side, ang = c["base"], c["side"], math.radians(c["angle_deg"])
        dx, dy = side * math.cos(ang), side * math.sin(ang)
        pts = [(-base/2, 0), (base/2, 0), (base/2 + dx, dy), (-base/2 + dx, dy)]
        traces.append(line_trace([p[0] for p in pts + [pts[0]]],
                                 [p[1] for p in pts + [pts[0]]], CHART[1], 3))
    elif shape == "trapezoid":
        a, b, h = c["a"], c["b"], c["h"]
        pts = [(-b/2, 0), (b/2, 0), (a/2, h), (-a/2, h)]
        traces.append(line_trace([p[0] for p in pts + [pts[0]]],
                                 [p[1] for p in pts + [pts[0]]], CHART[1], 3))
    elif shape == "rhombus":
        p, q = c["p"], c["q"]
        pts = [(0, q/2), (p/2, 0), (0, -q/2), (-p/2, 0)]
        traces.append(line_trace([p[0] for p in pts + [pts[0]]],
                                 [p[1] for p in pts + [pts[0]]], CHART[1], 3))
    elif shape == "sector":
        r, theta = c["r"], math.radians(c["theta_deg"])
        ts = _linspace(0, theta, 60)
        xs = [r * math.cos(t) for t in ts]
        ys = [r * math.sin(t) for t in ts]
        traces.append(line_trace([0] + xs + [0], [0] + ys + [0], CHART[1], 3))
    elif shape == "polygon":
        v = c["vertices"]
        traces.append(line_trace([p[0] for p in v + [v[0]]],
                                 [p[1] for p in v + [v[0]]], CHART[1], 3))
    return {
        "data": traces,
        "layout": {
            "shapes": shapes,
            "annotations": annotations,
            "xaxis_range": [-15, 15],
            "yaxis_range": [-15, 15],
            "yaxis_scaleanchor": "x", "yaxis_scaleratio": 1,
        },
    }


def _transform(c):
    orig = c["original"]
    trans = c["transformed"]
    data = [
        # closed polygon: original
        line_trace([p[0] for p in orig] + [orig[0][0]],
                   [p[1] for p in orig] + [orig[0][1]], CHART[1], 3),
        # closed polygon: transformed
        line_trace([p[0] for p in trans] + [trans[0][0]],
                   [p[1] for p in trans] + [trans[0][1]], CHART[2], 3),
        # basis vectors
        line_trace([0, c["i_hat"][0]], [0, c["i_hat"][1]], CHART[4], 2),
        line_trace([0, c["j_hat"][0]], [0, c["j_hat"][1]], CHART[3], 2),
    ]
    shapes = [vline_shape(0, MUTED), hline_shape(0, MUTED)]
    all_pts = orig + trans + [(0, 0)] + [c["i_hat"], c["j_hat"]]
    xs = [p[0] for p in all_pts]
    ys = [p[1] for p in all_pts]
    xmin, xmax, ymin, ymax = _auto_range_xy(xs, ys, 0.4)
    return {
        "data": data,
        "layout": {
            "shapes": shapes,
            "annotations": [],
            "xaxis_range": [xmin, xmax],
            "yaxis_range": [ymin, ymax],
            "yaxis_scaleanchor": "x", "yaxis_scaleratio": 1,
        },
    }


_BUILDERS = {
    "linear": _linear,
    "quadratic": _quadratic,
    "trig": _trig,
    "derivative": _derivative,
    "integral": _integral,
    "geometry": _geometry,
    "transform": _transform,
}


def build_plot(module, computed, request=None):
    """Public entry point used by views."""
    if module not in _BUILDERS:
        raise ValueError(f"Unknown module: {module}")
    return _BUILDERS[module](computed)
