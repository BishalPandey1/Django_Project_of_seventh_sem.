"""Pure-Python math for the quadratics module. No Django imports."""

import math


PRESETS = [
    {"name": "y = x²",                  "params": {"a": 1,  "b": 0,  "c": 0}, "blurb": "Standard parabola, vertex at origin."},
    {"name": "y = x² − 4",              "params": {"a": 1,  "b": 0,  "c": -4}, "blurb": "Shifted down, roots at ±2."},
    {"name": "y = (x−1)² = x²−2x+1",    "params": {"a": 1,  "b": -2, "c": 1}, "blurb": "Perfect square, one repeated root."},
    {"name": "y = 2x² + 3x − 5",        "params": {"a": 2,  "b": 3,  "c": -5}, "blurb": "Opens up, two real roots."},
    {"name": "y = −(x²) + 4",           "params": {"a": -1, "b": 0,  "c": 4}, "blurb": "Inverted, max value 4."},
]
BOUNDS  = {"a": (-20, 20, 0.1), "b": (-20, 20, 0.1), "c": (-20, 20, 0.1)}
FORMULA = lambda a, b, c, **_kw: f"y = {a:.3f}·x² + {b:.3f}·x + {c:.3f}"


def compute(a, b, c):
    vx = -b / (2 * a) if a != 0 else 0.0
    vy = a * vx * vx + b * vx + c
    disc = b * b - 4 * a * c
    roots = []
    if a != 0 and disc >= 0:
        r = math.sqrt(disc)
        roots = sorted([(-b - r) / (2 * a), (-b + r) / (2 * a)])
    if disc > 0:
        nature = "Two real roots"
    elif disc == 0:
        nature = "One repeated root"
    else:
        nature = "No real roots"
    if a > 0:
        opens = "upward (∪)"
    elif a < 0:
        opens = "downward (∩)"
    else:
        opens = "—"
    y_intercept = c
    return {
        "fn": lambda x: a * x * x + b * x + c,
        "vertex_x": vx,
        "vertex_y": vy,
        "disc": disc,
        "roots": roots,
        "nature": nature,
        "opens": opens,
        "y_intercept": y_intercept,
        "a": a, "b": b, "c": c,
    }


def _fmt(x, nd=3):
    s = f"{x:.{nd}f}"
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return s or "0"


def _signed(n_s):
    """Format a number for substitution: '−5' for negatives, '+5' for positives."""
    if n_s.startswith("-"):
        return "−" + n_s[1:]
    return "+" + n_s


def steps(a, b, c, vertex_x, vertex_y, disc, roots, nature, opens, y_intercept, **_ignored):
    a_s, b_s, c_s = _fmt(a), _fmt(b), _fmt(c)
    b_signed = _signed(b_s)
    c_signed = _signed(c_s)
    s = [
        {"text": "Start from the standard form of a parabola.",
         "formula": "y = a·x² + b·x + c",
         "result": "y = a·x² + b·x + c"},
        {"text": "Substitute the current coefficients.",
         "substitution": f"y = {a_s}·x² {b_signed}·x {c_signed}",
         "result": f"y = {a_s}·x² {b_signed}·x {c_signed}",
         "result_bind": ("a", float(a))},
        {"text": "The axis of symmetry sits at the midpoint of the roots (or at the vertex).",
         "formula": "x_v = −b / (2a)",
         "substitution": f"x_v = −({b_s}) / (2·{a_s})",
         "result": f"x_v = {_fmt(vertex_x)}",
         "result_bind": ("a", float(a))},
        {"text": "Plug the vertex x back into the function for the y-coordinate.",
         "formula": "y_v = a·x_v² + b·x_v + c",
         "substitution": f"y_v = f({_fmt(vertex_x)})",
         "result": f"y_v = {_fmt(vertex_y)}",
         "result_bind": ("c", float(c))},
        {"text": "The y-intercept is the value of y when x = 0.",
         "formula": "y(0) = c",
         "substitution": f"y(0) = {c_s}",
         "result": f"c = {_fmt(y_intercept)}",
         "result_bind": ("c", float(c))},
        {"text": f"The parabola opens {opens}.",
         "formula": "a > 0 ⇒ ∪ ;  a < 0 ⇒ ∩",
         "result": opens,
         "result_bind": ("a", float(a))},
        {"text": "Discriminant determines the nature of the roots.",
         "formula": "Δ = b² − 4ac",
         "substitution": f"Δ = ({b_s})² − 4·{a_s}·{c_s}",
         "result": f"Δ = {_fmt(disc)}  →  {nature}",
         "result_bind": ("c", float(c))},
    ]
    if roots:
        if len(roots) == 2 and abs(roots[0] - roots[1]) > 1e-9:
            s.append({
                "text": "Apply the quadratic formula to find the x-intercepts.",
                "formula": "x = (−b ± √Δ) / (2a)",
                "substitution": f"x = (−({b_s}) ± √{_fmt(disc)}) / (2·{a_s})",
                "result": "x ∈ {" + ", ".join(f"{_fmt(r)}" for r in roots) + "}",
                "result_bind": ("a", float(a)),
            })
        else:
            s.append({
                "text": "The discriminant is zero — there is a single repeated root.",
                "formula": "x = −b / (2a)",
                "substitution": f"x = −({b_s}) / (2·{a_s})",
                "result": f"x = {_fmt(roots[0])} (repeated)",
                "result_bind": ("a", float(a)),
            })
    else:
        s.append({"text": "No real x-intercepts — the curve never crosses the x-axis.",
                  "formula": "Δ < 0  →  no real roots",
                  "result": "x = ∅"})
    return s


def solvers(_params=None):
    return {
        "vars": [
            {"symbol": "a", "label": "a", "color": "#3b82f6"},
            {"symbol": "b", "label": "b", "color": "#a855f7"},
            {"symbol": "c", "label": "c", "color": "#f59e0b"},
            {"symbol": "x", "label": "x", "color": "#06b6d4"},
            {"symbol": "y", "label": "y", "color": "#ec4899"},
        ],
        "solvers": {
            "y": {"formula": "y = a·x² + b·x + c",
                  "compute_js": "a*x*x + b*x + c"},
            "x": {"formula": "x = (−b + √(b² − 4a(c−y))) / (2a)",
                  "compute_js": "(-b + Math.sqrt(b*b - 4*a*(c-y))) / (2*a)"},
        },
    }
