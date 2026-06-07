"""Pure-Python math for the linear-functions module. No Django imports."""

import math


PRESETS = [
    {"name": "y = x",            "params": {"m": 1,  "b": 0}, "blurb": "Identity — 45° line."},
    {"name": "y = 2x + 1",       "params": {"m": 2,  "b": 1}, "blurb": "Slope 2, crosses y at 1."},
    {"name": "y = −x + 3",       "params": {"m": -1, "b": 3}, "blurb": "Falling line, y-int 3."},
    {"name": "Horizontal y = 5", "params": {"m": 0,  "b": 5}, "blurb": "Zero slope, parallel to x-axis."},
    {"name": "Vertical-ish 10x", "params": {"m": 10, "b": 0}, "blurb": "Steep slope of 10."},
]
BOUNDS  = {"m": (-50, 50, 0.1), "b": (-50, 50, 0.1)}
FORMULA = lambda m, b, **_kw: f"y = {m:.3f}·x + {b:.3f}"


def compute(m, b):
    """Return keys, intercepts, slope angle, and a fn(x) callable."""
    return {
        "fn": lambda x: m * x + b,
        "x_intercept": (-b / m) if m != 0 else float("nan"),
        "y_intercept": b,
        "angle_deg": math.degrees(math.atan(m)),
        "slope": m,
        "distance": abs(b) / math.sqrt(m * m + 1) if m != 0 else abs(b),
    }


def _fmt(x, nd=3):
    """Format a number with `nd` decimals, stripping trailing zeros/point."""
    s = f"{x:.{nd}f}"
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return s or "0"


def steps(m, b, x_intercept, angle_deg, distance, **_ignored):
    """Build the linear-function step-by-step solution.

    Every result has a ``result_bind`` so the solution editor can apply
    edits back to the right input on the Input board.
    """
    m_s, b_s = _fmt(m), _fmt(b)
    s = [
        {"text": "Start from the slope-intercept form of a line.",
         "formula": "y = m·x + b",
         "result": "y = m·x + b"},
        {"text": "Substitute the current slope and intercept.",
         "substitution": f"y = {m_s}·x + {b_s}",
         "result": f"y = {m_s}·x + {b_s}",
         "result_bind": ("m", float(m))},
        {"text": "The y-intercept is the value of y when x = 0.",
         "formula": "y(0) = m·(0) + b = b",
         "substitution": f"y(0) = {m_s}·(0) + {b_s}",
         "result": f"b = {_fmt(b)}",
         "result_bind": ("b", float(b))},
    ]
    if m != 0:
        s.append({
            "text": "The x-intercept is where y = 0. Solve 0 = m·x + b for x.",
            "formula": "x = −b / m",
            "substitution": f"x = −({b_s}) / {m_s}",
            "result": f"x = {_fmt(x_intercept)}",
            "result_bind": ("m", float(m)),
        })
    else:
        s.append({"text": "When the slope is zero the line is horizontal — "
                          "it never crosses the x-axis (unless b is also 0).",
                  "result": "no x-intercept"})
    s.append({
        "text": "The slope is the tangent of the angle the line makes with the x-axis.",
        "formula": "θ = arctan(m)",
        "substitution": f"θ = arctan({m_s})",
        "result": f"θ ≈ {_fmt(angle_deg, 2)}°",
        "result_bind": ("m", float(m)),
    })
    s.append({
        "text": "The distance formula gives the perpendicular distance from origin to the line.",
        "formula": "d = |b| / √(m² + 1)",
        "substitution": f"d = |{b_s}| / √({m_s}² + 1)",
        "result": f"d ≈ {_fmt(distance)}",
        "result_bind": ("b", float(b)),
    })
    return s


def solvers(_params=None):
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
