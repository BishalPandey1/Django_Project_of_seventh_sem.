"""Pure-Python math for the sine-waves module. No Django imports."""

import math


PRESETS = [
    {"name": "sin(x)",        "params": {"A": 1,  "B": 1,        "C": 0,  "D": 0}, "blurb": "Classic sine, period 2π."},
    {"name": "cos(x)",        "params": {"A": 1,  "B": 1,        "C": -1.5708, "D": 0}, "blurb": "Cosine (sine shifted left by π/2)."},
    {"name": "2·sin(x)",      "params": {"A": 2,  "B": 1,        "C": 0,  "D": 0}, "blurb": "Amplitude doubled."},
    {"name": "sin(2x)",       "params": {"A": 1,  "B": 2,        "C": 0,  "D": 0}, "blurb": "Frequency doubled, period π."},
    {"name": "−sin(x) + 3",   "params": {"A": -1, "B": 1,        "C": 0,  "D": 3}, "blurb": "Flipped, midline at y = 3."},
    {"name": "0.5·sin(0.5x)−1", "params": {"A": 0.5, "B": 0.5,   "C": 0,  "D": -1}, "blurb": "Slow wave around y = −1."},
]
BOUNDS  = {"A": (-10, 10, 0.1), "B": (-10, 10, 0.05), "C": (-12.57, 12.57, 0.1), "D": (-10, 10, 0.1)}
FORMULA = lambda A, B, C, D, **_kw: f"y = {A:.3f}·sin({B:.3f}·x + {C:.3f}) + {D:.3f}"


def compute(A, B, C, D):
    if B != 0:
        period = 2 * math.pi / abs(B)
        shift = -C / B
    else:
        period = float("inf")
        shift = 0.0
    return {
        "fn": lambda x: A * math.sin(B * x + C) + D,
        "period": period,
        "phase_shift": shift,
        "amplitude": abs(A),
        "midline": D,
        "frequency": abs(B) / (2 * math.pi),
        "max_value": abs(A) + D,
        "min_value": -abs(A) + D,
        "A": A, "B": B, "C": C, "D": D,
    }


def _fmt(x, nd=3):
    s = f"{x:.{nd}f}"
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    if not s or s == "-":
        s = "0"
    return s


def _signed(n_s):
    if n_s.startswith("-"):
        return "−" + n_s[1:]
    return "+" + n_s


def steps(A, B, C, D, period, phase_shift, amplitude, midline, frequency,
          max_value, min_value, **_ignored):
    A_s, B_s, C_s, D_s = _fmt(A), _fmt(B), _fmt(C), _fmt(D)
    D_sign = f"−{D_s[1:]}" if D < 0 else _signed(D_s)
    s = [
        {"text": "Start from the general form of a sinusoid.",
         "formula": "y = A·sin(B·x + C) + D",
         "result": "y = A·sin(B·x + C) + D"},
        {"text": "Substitute the current parameters.",
         "substitution": f"y = {A_s}·sin({B_s}·x {_signed(C_s)}) {D_sign}",
         "result": f"y = {A_s}·sin({B_s}·x {_signed(C_s)}) {D_sign}",
         "result_bind": ("A", float(A))},
        {"text": "The amplitude is |A| — the curve oscillates that far from the midline.",
         "formula": "amp = |A|",
         "substitution": f"amp = |{A_s}|",
         "result": f"amp = {_fmt(amplitude)}",
         "result_bind": ("A", float(A))},
        {"text": "The period is the horizontal length of one full cycle.",
         "formula": "T = 2π / |B|",
         "substitution": f"T = 2π / |{B_s}|",
         "result": (f"T = {'∞' if math.isinf(period) else _fmt(period)}"),
         "result_bind": ("B", float(B))},
        {"text": "The frequency is the number of full cycles per unit of x.",
         "formula": "f = |B| / (2π)",
         "substitution": f"f = |{B_s}| / (2π)",
         "result": f"f = {_fmt(frequency, 4)}",
         "result_bind": ("B", float(B))},
    ]
    if B != 0:
        s.append({
            "text": "The phase shift is the horizontal translation of the curve.",
            "formula": "shift = −C / B",
            "substitution": f"shift = −({C_s}) / {B_s}",
            "result": f"shift = {_fmt(phase_shift)}",
            "result_bind": ("C", float(C)),
        })
    else:
        s.append({
            "text": "B = 0 means the argument of sin is constant — the curve is a flat line at A·sin(C) + D.",
            "formula": "B = 0  →  y = A·sin(C) + D  (constant)",
            "result": "y = constant",
        })
    s.append({
        "text": "D is the midline — the y-value the curve oscillates around.",
        "formula": "midline = D",
        "substitution": f"midline = {D_s}",
        "result": f"midline = {_fmt(midline)}",
        "result_bind": ("D", float(D)),
    })
    s.append({
        "text": "Maximum and minimum y-values reached by the curve.",
        "formula": "y_max = D + |A| ,  y_min = D − |A|",
        "result": f"y_max = {_fmt(max_value)} ,  y_min = {_fmt(min_value)}",
        "result_bind": ("A", float(A)),
    })
    return s


def solvers(_params=None):
    return {
        "vars": [
            {"symbol": "A", "label": "amplitude",   "color": "#3b82f6"},
            {"symbol": "B", "label": "frequency",   "color": "#a855f7"},
            {"symbol": "C", "label": "phase",       "color": "#f59e0b"},
            {"symbol": "D", "label": "midline",     "color": "#10b981"},
            {"symbol": "x", "label": "input",       "color": "#06b6d4"},
            {"symbol": "y", "label": "output",      "color": "#ec4899"},
        ],
        "solvers": {
            "y": {"formula": "y = A·sin(B·x + C) + D",
                  "compute_js": "A*Math.sin(B*x + C) + D"},
            "x": {"formula": "x = (asin((y − D) / A) − C) / B",
                  "compute_js": "(Math.asin((y - D) / A) - C) / B"},
        },
    }
