"""Pure-Python math for the integrals module. No Django imports."""

import math


FUNCTIONS = {
    "poly": {"fn": lambda x: x * x / 4,         "label": "f(x)=x²/4",        "antideriv": "F(x)=x³/12"},
    "quad": {"fn": lambda x: -x * x + 9,        "label": "f(x)=−x²+9",       "antideriv": "F(x)=−x³/3+9x"},
    "sin":  {"fn": lambda x: 2 * math.sin(x) + 3, "label": "f(x)=2·sin(x)+3", "antideriv": "F(x)=−2·cos(x)+3x"},
    "exp":  {"fn": lambda x: math.exp(x / 3),   "label": "f(x)=e^(x/3)",     "antideriv": "F(x)=3·e^(x/3)"},
}

METHODS = ["left", "right", "midpoint", "trapezoid"]


def compute(fn_key, a, b, n, method):
    f = FUNCTIONS[fn_key]["fn"]
    if n < 1:
        n = 1
    if a == b:
        return {
            "fn": f, "label": FUNCTIONS[fn_key]["label"],
            "antideriv": FUNCTIONS[fn_key]["antideriv"],
            "dx": 0.0, "riemann": 0.0, "exact": 0.0, "error": 0.0, "bars": [],
        }
    dx = (b - a) / n
    riemann = 0.0
    bars = []
    for i in range(n):
        x1, x2 = a + i * dx, a + (i + 1) * dx
        if method == "left":
            y = f(x1)
        elif method == "right":
            y = f(x2)
        elif method == "midpoint":
            y = f((x1 + x2) / 2)
        else:  # trapezoid mid-height
            y = (f(x1) + f(x2)) / 2
        riemann += y * dx
        bars.append({"x1": x1, "x2": x2, "y": y, "method": method})
    # exact via dense trapezoid
    N = 5000
    dxx = (b - a) / N
    exact = 0.0
    for i in range(N):
        x1, x2 = a + i * dxx, a + (i + 1) * dxx
        exact += (f(x1) + f(x2)) / 2 * dxx
    return {
        "fn": f, "label": FUNCTIONS[fn_key]["label"],
        "antideriv": FUNCTIONS[fn_key]["antideriv"],
        "dx": dx, "riemann": riemann, "exact": exact, "error": riemann - exact,
        "bars": bars,
    }


def steps(fn_key, a, b, n, method, dx, riemann, exact, error, **_ignored):
    info = FUNCTIONS[fn_key]
    return [
        {"text": "Choose the integrand.",
         "formula": info["label"], "result": info["antideriv"]},
        {"text": "Split the interval [a, b] into n equal subintervals.",
         "formula": "Δx = (b − a) / n",
         "substitution": f"Δx = ({b:.2f} − {a:.2f}) / {n}",
         "result": f"Δx = {dx:.4f}",
         "result_bind": ("b", float(b))},
        {"text": f"Apply the {method}-endpoint Riemann rule on each subintervals.",
         "formula": "R = Σ f(x*) · Δx",
         "result": f"R ≈ {riemann:.4f}",
         "result_bind": ("n", float(n))},
        {"text": "The exact area is approximated with a high-resolution trapezoid.",
         "formula": "A = ∫[a,b] f(x) dx ≈ Σ (f(xᵢ)+f(xᵢ₊₁))/2 · Δx",
         "result": f"A ≈ {exact:.4f}"},
        {"text": "Compare the two.",
         "formula": "error = R − A",
         "result": f"error ≈ {error:.4f}"},
    ]


def solvers():
    return {
        "vars": [
            {"symbol": "a", "label": "a",     "color": "#3b82f6"},
            {"symbol": "b", "label": "b",     "color": "#a855f7"},
            {"symbol": "n", "label": "n",     "color": "#f59e0b"},
            {"symbol": "A", "label": "area",  "color": "#10b981"},
        ],
        "solvers": {
            "A": {"formula": "A ≈ (b − a) · f((a+b)/2)", "compute_js": "(b - a) * ((a + b) / 2) * ((a + b) / 2) / 4"},
        },
    }


def functions_meta():
    return [{"key": k, "label": v["label"], "antideriv": v["antideriv"]} for k, v in FUNCTIONS.items()]


def methods_meta():
    return [{"key": m, "label": m.capitalize()} for m in METHODS]
