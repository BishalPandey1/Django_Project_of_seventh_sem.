"""Pure-Python math for the linear-functions module. No Django imports."""

import math


def compute(m, b):
    """Return keys, intercepts, slope angle, and a fn(x) callable."""
    return {
        "fn": lambda x: m * x + b,
        "x_intercept": (-b / m) if m != 0 else float("nan"),
        "y_intercept": b,
        "angle_deg": math.degrees(math.atan(m)),
        "slope": m,
    }


def steps(m, b, x_intercept, angle_deg, **_ignored):
    s = [
        {"text": "Start from the slope-intercept form of a line.",
         "formula": "y = m·x + b"},
        {"text": "Substitute the current slope and intercept.",
         "substitution": f"y = {m:.2f}·x + ({b:.2f})"},
        {"text": "The y-intercept is the value of y when x = 0.",
         "formula": "y(0) = b",
         "substitution": f"y(0) = {b:.3f})",
         "result": f"b = {b:.3f}",
         "result_bind": ("b", float(b))},
    ]
    if m != 0:
        s.append({
            "text": "The x-intercept is where y = 0. Solve 0 = m·x + b.",
            "formula": "x = −b / m",
            "substitution": f"x = −({b:.2f}) / {m:.2f}",
            "result": f"x = {x_intercept:.3f}",
        })
    else:
        s.append({"text": "When the slope is zero the line is horizontal — "
                          "it never crosses the x-axis (unless b is also 0)."})
    s.append({
        "text": "The slope is the tangent of the angle the line makes with the x-axis.",
        "formula": "θ = arctan(m)",
        "substitution": f"θ = arctan({m:.3f})",
        "result": f"θ ≈ {angle_deg:.2f}°",
    })
    return s


def solvers():
    return {
        "vars": [
            {"symbol": "m", "label": "slope",       "color": "#3b82f6"},
            {"symbol": "b", "label": "y-intercept", "color": "#f59e0b"},
            {"symbol": "x", "label": "input",       "color": "#06b6d4"},
            {"symbol": "y", "label": "output",      "color": "#a855f7"},
        ],
        "solvers": {
            "y": {"formula": "y = m·x + b",   "compute_js": "m*x + b"},
            "x": {"formula": "x = (y − b) / m", "compute_js": "(y - b) / m"},
            "m": {"formula": "m = (y − b) / x", "compute_js": "(y - b) / x"},
            "b": {"formula": "b = y − m·x",     "compute_js": "y - m*x"},
        },
    }
