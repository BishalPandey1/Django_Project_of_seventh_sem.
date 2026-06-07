"""Pure-Python math for the derivatives module. No Django imports."""

import math


FUNCTIONS = {
    "poly":  {"fn": lambda x: x * x,            "label": "f(x)=x²",        "deriv": "f′(x)=2x"},
    "cubic": {"fn": lambda x: x ** 3 - 3 * x,   "label": "f(x)=x³-3x",     "deriv": "f′(x)=3x²-3"},
    "sin":   {"fn": lambda x: math.sin(x),      "label": "f(x)=sin(x)",    "deriv": "f′(x)=cos(x)"},
    "exp":   {"fn": lambda x: math.exp(x / 3),  "label": "f(x)=e^(x/3)",   "deriv": "f′(x)=(1/3)·e^(x/3)"},
    "abs":   {"fn": lambda x: abs(x),           "label": "f(x)=|x|",       "deriv": "f′(x)=sign(x)"},
}


def compute(fn_key, x0, h):
    f = FUNCTIONS[fn_key]["fn"]
    y0 = f(x0)
    slope_exact = (f(x0 + 1e-6) - f(x0 - 1e-6)) / 2e-6
    slope_secant = (f(x0 + h) - f(x0)) / h
    return {
        "fn": f,
        "label": FUNCTIONS[fn_key]["label"],
        "deriv": FUNCTIONS[fn_key]["deriv"],
        "y0": y0,
        "slope_exact": slope_exact,
        "slope_secant": slope_secant,
        "error": abs(slope_exact - slope_secant),
        "tangent_fn": lambda x, _s=slope_exact, _y=y0: _s * (x - x0) + _y,
        "secant_fn":  lambda x, _s=slope_secant, _y=y0: _s * (x - x0) + _y,
    }


def steps(fn_key, x0, h, y0, slope_exact, slope_secant, error, **_ignored):
    info = FUNCTIONS[fn_key]
    return [
        {"text": "Choose the parent function to study.",
         "formula": info["label"], "result": info["deriv"]},
        {"text": "Evaluate the function at the point of interest.",
         "formula": f"f({x0:.3f})",
         "substitution": f"f({x0:.3f})",
         "result": f"y₀ = {y0:.3f}",
         "result_bind": ("x0", float(x0))},
        {"text": "The derivative is the limit of the difference quotient.",
         "formula": "f′(x₀) = lim[h→0] (f(x₀+h) − f(x₀)) / h"},
        {"text": "The secant slope approximates the derivative with a finite h.",
         "formula": "m_sec = (f(x₀+h) − f(x₀)) / h",
         "substitution": f"h = {h:.3f}",
         "result": f"m_sec ≈ {slope_secant:.4f}",
         "result_bind": ("h", float(h))},
        {"text": "A symmetric difference quotient with a tiny h gives the exact slope.",
         "formula": "m_exact = (f(x₀+ε) − f(x₀−ε)) / (2ε),  ε=1e-6",
         "result": f"m_exact ≈ {slope_exact:.4f}"},
        {"text": "The error shrinks as h → 0.",
         "formula": "error = |m_exact − m_sec|",
         "result": f"error ≈ {error:.2e}"},
    ]


def solvers():
    return {
        "vars": [
            {"symbol": "x0", "label": "x₀",      "color": "#3b82f6"},
            {"symbol": "h",  "label": "step h",  "color": "#a855f7"},
            {"symbol": "y",  "label": "y",       "color": "#f59e0b"},
        ],
        "solvers": {
            "y":  {"formula": "y = f(x₀)", "compute_js": "x0*x0"},
            "h":  {"formula": "h ≈ 0",     "compute_js": "0.01"},
        },
    }


def functions_meta():
    return [{"key": k, "label": v["label"], "deriv": v["deriv"]} for k, v in FUNCTIONS.items()]
