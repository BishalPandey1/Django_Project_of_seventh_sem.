"""Pure-Python math for the derivatives module. No Django imports."""

import math


FUNCTIONS = {
    "poly":  {"fn": lambda x: x * x,            "label": "f(x)=x²",         "deriv": "f′(x)=2x",
              "fn_js": "x0*x0", "deriv_js": "2*x0"},
    "cubic": {"fn": lambda x: x ** 3 - 3 * x,   "label": "f(x)=x³−3x",      "deriv": "f′(x)=3x²−3",
              "fn_js": "x0*x0*x0 - 3*x0", "deriv_js": "3*x0*x0 - 3"},
    "sin":   {"fn": lambda x: math.sin(x),      "label": "f(x)=sin(x)",     "deriv": "f′(x)=cos(x)",
              "fn_js": "Math.sin(x0)", "deriv_js": "Math.cos(x0)"},
    "exp":   {"fn": lambda x: math.exp(x / 3),  "label": "f(x)=e^(x/3)",    "deriv": "f′(x)=(1/3)·e^(x/3)",
              "fn_js": "Math.exp(x0/3)", "deriv_js": "(1/3)*Math.exp(x0/3)"},
    "abs":   {"fn": lambda x: abs(x),           "label": "f(x)=|x|",        "deriv": "f′(x)=sign(x)",
              "fn_js": "Math.abs(x0)", "deriv_js": "x0 >= 0 ? 1 : -1"},
}

PRESETS = [
    {"name": "x² at 3",   "params": {"fn_key": "poly",  "x0": 3,   "h": 0.5}, "blurb": "Slope 6 at x = 3."},
    {"name": "x² at −2",  "params": {"fn_key": "poly",  "x0": -2,  "h": 0.5}, "blurb": "Slope −4 at x = −2."},
    {"name": "x³−3x at 2", "params": {"fn_key": "cubic", "x0": 2,  "h": 0.5}, "blurb": "Local min/max region."},
    {"name": "sin(x) at 0", "params": {"fn_key": "sin",  "x0": 0,  "h": 0.5}, "blurb": "Slope 1 at the origin."},
    {"name": "e^(x/3) at 0", "params": {"fn_key": "exp", "x0": 0,  "h": 0.1}, "blurb": "Slope 1/3 at the origin."},
    {"name": "|x| at 0",  "params": {"fn_key": "abs",   "x0": 0,   "h": 0.5}, "blurb": "Corner — secant sensitive to h."},
]
BOUNDS  = {"x0": (-10, 10, 0.05), "h": (0.001, 5, 0.01)}
FORMULA = lambda fn_key, x0, h, **_kw: (
    f"f(x) = {FUNCTIONS[fn_key]['label']},  x₀ = {x0:.3f},  h = {h:.3f}"
)


def compute(fn_key, x0, h):
    info = FUNCTIONS[fn_key]
    f = info["fn"]
    y0 = f(x0)
    slope_exact = (f(x0 + 1e-6) - f(x0 - 1e-6)) / 2e-6
    slope_secant = (f(x0 + h) - f(x0)) / h
    return {
        "fn": f,
        "label": info["label"],
        "deriv": info["deriv"],
        "y0": y0,
        "x0": x0,
        "h": h,
        "slope_exact": slope_exact,
        "slope_secant": slope_secant,
        "error": abs(slope_exact - slope_secant),
        "tangent_fn": lambda x, _s=slope_exact, _y=y0: _s * (x - x0) + _y,
        "secant_fn":  lambda x, _s=slope_secant, _y=y0: _s * (x - x0) + _y,
    }


def _fmt(x, nd=3):
    s = f"{x:.{nd}f}"
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return s or "0"


def steps(fn_key, x0, h, y0, slope_exact, slope_secant, error, **_ignored):
    info = FUNCTIONS[fn_key]
    x0_s, h_s = _fmt(x0), _fmt(h)
    return [
        {"text": "Choose the parent function to study.",
         "formula": info["label"], "result": info["deriv"]},
        {"text": "Evaluate the function at the point of interest.",
         "formula": f"y₀ = f(x₀)",
         "substitution": f"y₀ = f({x0_s})",
         "result": f"y₀ = {_fmt(y0)}",
         "result_bind": ("x0", float(x0))},
        {"text": "The derivative is the limit of the difference quotient.",
         "formula": "f′(x₀) = lim[h→0] (f(x₀+h) − f(x₀)) / h",
         "result": "f′(x₀) = lim[h→0] (f(x₀+h) − f(x₀)) / h"},
        {"text": "The secant slope approximates the derivative with a finite h.",
         "formula": "m_sec = (f(x₀+h) − f(x₀)) / h",
         "substitution": f"m_sec = (f({x0_s}+{h_s}) − f({x0_s})) / {h_s}",
         "result": f"m_sec ≈ {_fmt(slope_secant, 4)}",
         "result_bind": ("h", float(h))},
        {"text": "A symmetric difference quotient with a tiny h gives the exact slope.",
         "formula": "m_exact = (f(x₀+ε) − f(x₀−ε)) / (2ε),  ε=1e-6",
         "result": f"m_exact ≈ {_fmt(slope_exact, 4)}",
         "result_bind": ("h", float(h))},
        {"text": "The tangent line at x₀ has the same slope as the derivative.",
         "formula": "tangent:  y = m_exact·(x − x₀) + y₀",
         "substitution": f"y ≈ {_fmt(slope_exact, 4)}·(x − {x0_s}) + {_fmt(y0)}",
         "result": f"y ≈ {_fmt(slope_exact, 4)}·(x − {x0_s}) + {_fmt(y0)}"},
        {"text": "The error shrinks as h → 0.",
         "formula": "error = |m_exact − m_sec|",
         "result": f"error ≈ {error:.2e}",
         "result_bind": ("h", float(h))},
    ]


def solvers(params=None):
    """Parametric solvers — depend on the currently selected function."""
    fn_key = (params or {}).get("fn_key", "poly")
    info = FUNCTIONS.get(fn_key, FUNCTIONS["poly"])
    fn_js = info["fn_js"]
    deriv_js = info["deriv_js"]
    return {
        "vars": [
            {"symbol": "x0",  "label": "x₀",     "color": "#3b82f6"},
            {"symbol": "h",   "label": "step h", "color": "#a855f7"},
            {"symbol": "y",   "label": "y",      "color": "#f59e0b"},
            {"symbol": "m",   "label": "slope",  "color": "#10b981"},
        ],
        "solvers": {
            "y": {"formula": f"y = f(x₀)  →  {info['label']}",
                  "compute_js": fn_js},
            "m": {"formula": f"m = f′(x₀)  →  {info['deriv']}",
                  "compute_js": deriv_js},
            "h": {"formula": "h ≈ 0 (small step)", "compute_js": "0.01"},
        },
    }


def functions_meta():
    return [{"key": k, "label": v["label"], "deriv": v["deriv"]} for k, v in FUNCTIONS.items()]
