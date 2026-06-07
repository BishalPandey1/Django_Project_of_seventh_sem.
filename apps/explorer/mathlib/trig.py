"""Pure-Python math for the sine-waves module. No Django imports."""

import math


def compute(A, B, C, D):
    period = (2 * math.pi / abs(B)) if B != 0 else float("inf")
    shift = -C / (B if B != 0 else 1e-4)
    return {
        "fn": lambda x: A * math.sin(B * x + C) + D,
        "period": period,
        "phase_shift": shift,
        "amplitude": abs(A),
        "midline": D,
        "A": A, "B": B, "C": C, "D": D,
    }


def steps(A, B, C, D, period, phase_shift, amplitude, midline, **_ignored):
    s = [
        {"text": "Start from the general form of a sinusoid.",
         "formula": "y = A·sin(B·x + C) + D"},
        {"text": "Substitute the current parameters.",
         "substitution": f"y = {A:.2f}·sin({B:.2f}·x + {C:.2f}) + {D:.2f}"},
        {"text": "The amplitude is |A|; the curve oscillates that far from the midline.",
         "formula": "amp = |A|",
         "result": f"amp = {amplitude:.3f}",
         "result_bind": ("A", float(A))},
        {"text": "The period is the horizontal length of one full cycle.",
         "formula": "T = 2π / |B|",
         "substitution": f"T = 2π / |{B:.2f}|",
         "result": f"T = {period:.3f}",
         "result_bind": ("B", float(B))},
        {"text": "The phase shift is the horizontal translation of the curve.",
         "formula": "shift = −C / B",
         "substitution": f"shift = −({C:.2f}) / {B:.2f}",
         "result": f"shift = {phase_shift:.3f}",
         "result_bind": ("C", float(C))},
        {"text": "D is the midline — the y-value the curve oscillates around.",
         "formula": "midline = D",
         "result": f"midline = {midline:.3f}",
         "result_bind": ("D", float(D))},
    ]
    return s


def solvers():
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
