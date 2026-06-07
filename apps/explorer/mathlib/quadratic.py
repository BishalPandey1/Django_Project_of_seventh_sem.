"""Pure-Python math for the quadratics module. No Django imports."""

import math


def compute(a, b, c):
    vx = -b / (2 * a) if a != 0 else 0.0
    vy = a * vx * vx + b * vx + c
    disc = b * b - 4 * a * c
    roots = []
    if a != 0 and disc >= 0:
        r = math.sqrt(disc)
        roots = [(-b - r) / (2 * a), (-b + r) / (2 * a)]
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
    return {
        "fn": lambda x: a * x * x + b * x + c,
        "vertex_x": vx,
        "vertex_y": vy,
        "disc": disc,
        "roots": roots,
        "nature": nature,
        "opens": opens,
        "a": a, "b": b, "c": c,
    }


def steps(a, b, c, vertex_x, vertex_y, disc, roots, nature, opens, **_ignored):
    s = [
        {"text": "Start from the standard form of a parabola.",
         "formula": "y = a·x² + b·x + c"},
        {"text": "Substitute the current coefficients.",
         "substitution": f"y = {a:.2f}·x² + {b:.2f}·x + {c:.2f}"},
        {"text": "The vertex lies on the axis of symmetry.",
         "formula": "x_v = −b / (2a)",
         "substitution": f"x_v = −({b:.2f}) / (2·{a:.2f})",
         "result": f"x_v = {vertex_x:.3f}",
         "result_bind": ("b", float(b))},
        {"text": "Plug the vertex x back into the function for the y-coordinate.",
         "formula": "y_v = a·x_v² + b·x_v + c",
         "substitution": f"y_v = f({vertex_x:.3f})",
         "result": f"y_v = {vertex_y:.3f}",
         "result_bind": ("c", float(c))},
        {"text": f"The parabola opens {opens}.",
         "formula": "a > 0 ⇒ ∪ ; a < 0 ⇒ ∩"},
        {"text": "Discriminant determines the nature of the roots.",
         "formula": "Δ = b² − 4ac",
         "substitution": f"Δ = {b:.2f}² − 4·{a:.2f}·{c:.2f}",
         "result": f"Δ = {disc:.3f}  →  {nature}"},
    ]
    if roots:
        s.append({
            "text": "Apply the quadratic formula to find the x-intercepts.",
            "formula": "x = (−b ± √Δ) / (2a)",
            "result": "x ∈ {" + ", ".join(f"{r:.3f}" for r in roots) + "}",
        })
    else:
        s.append({"text": "No real x-intercepts (the curve never crosses the x-axis)."})
    return s


def solvers():
    return {
        "vars": [
            {"symbol": "a", "label": "a", "color": "#3b82f6"},
            {"symbol": "b", "label": "b", "color": "#a855f7"},
            {"symbol": "c", "label": "c", "color": "#f59e0b"},
            {"symbol": "x", "label": "x", "color": "#06b6d4"},
            {"symbol": "y", "label": "y", "color": "#ec4899"},
        ],
        "solvers": {
            "y": {"formula": "y = a·x² + b·x + c", "compute_js": "a*x*x + b*x + c"},
            "x": {"formula": "x = (−b ± √(b² − 4a(c−y))) / (2a)",
                  "compute_js": "(-b + Math.sqrt(b*b - 4*a*(c-y))) / (2*a)"},
        },
    }
