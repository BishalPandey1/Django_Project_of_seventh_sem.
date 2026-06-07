"""Pure-Python math for the integrals module. No Django imports."""

import math


FUNCTIONS = {
    "poly": {"fn": lambda x: x * x / 4,         "label": "f(x)=x²/4",        "antideriv": "F(x)=x³/12",
             "fn_js": "x*x/4"},
    "quad": {"fn": lambda x: -x * x + 9,        "label": "f(x)=−x²+9",       "antideriv": "F(x)=−x³/3+9x",
             "fn_js": "-x*x + 9"},
    "sin":  {"fn": lambda x: 2 * math.sin(x) + 3, "label": "f(x)=2·sin(x)+3", "antideriv": "F(x)=−2·cos(x)+3x",
             "fn_js": "2*Math.sin(x) + 3"},
    "exp":  {"fn": lambda x: math.exp(x / 3),   "label": "f(x)=e^(x/3)",     "antideriv": "F(x)=3·e^(x/3)",
             "fn_js": "Math.exp(x/3)"},
}

METHODS = ["left", "right", "midpoint", "trapezoid"]

PRESETS = [
    {"name": "x²/4 on [0, 4]",         "params": {"fn_key": "poly", "a": 0,   "b": 4,     "n": 20,  "method": "midpoint"},  "blurb": "Parabola area, exact 16/3."},
    {"name": "−x²+9 on [−3, 3]",       "params": {"fn_key": "quad", "a": -3,  "b": 3,     "n": 30,  "method": "midpoint"},  "blurb": "Inverted parabola, exact 36."},
    {"name": "2·sin(x)+3 on [0, π]",   "params": {"fn_key": "sin",  "a": 0,   "b": 3.1416, "n": 40, "method": "trapezoid"}, "blurb": "One hump of a sinusoid."},
    {"name": "e^(x/3) on [0, 6]",      "params": {"fn_key": "exp",  "a": 0,   "b": 6,     "n": 25,  "method": "midpoint"},  "blurb": "Exponential growth."},
    {"name": "x²/4, n = 200",          "params": {"fn_key": "poly", "a": 0,   "b": 4,     "n": 200, "method": "midpoint"},  "blurb": "Many rectangles → exact value."},
]
BOUNDS  = {"a": (-20, 20, 0.1), "b": (-20, 20, 0.1), "n": (1, 500, 1)}
FORMULA = lambda fn_key, a, b, n, method, **_kw: (
    f"∫[{a:.3f}, {b:.3f}] {FUNCTIONS[fn_key]['label']} dx,  n = {n},  {method}"
)


def _riemann_js(fn_js, method):
    """Build a JS expression that computes the Riemann sum for fn_js and method.

    The returned expression is wrapped in an IIFE so it can `return`. It
    depends on the variables ``a``, ``b``, ``n`` being in scope (the JS solver
    panel provides them).
    """
    if method == "trapezoid":
        return (
            "(function(){"
            "var fn=function(x){return " + fn_js + ";};"
            "var dx=(b-a)/n,_s=0,i;"
            "for(i=0;i<n;i++){"
            "  var x1=a+i*dx,x2=a+(i+1)*dx;"
            "  _s+=(fn(x1)+fn(x2))/2*dx;"
            "}"
            "return _s;"
            "})()"
        )
    if method == "midpoint":
        pick = "(x1+x2)/2"
    elif method == "left":
        pick = "x1"
    else:  # right
        pick = "x2"
    return (
        "(function(){"
        "var fn=function(x){return " + fn_js + ";};"
        "var dx=(b-a)/n,_s=0,i;"
        "for(i=0;i<n;i++){"
        "  var x1=a+i*dx,x2=a+(i+1)*dx,x=" + pick + ";"
        "  _s+=fn(x)*dx;"
        "}"
        "return _s;"
        "})()"
    )


def compute(fn_key, a, b, n, method):
    f = FUNCTIONS[fn_key]["fn"]
    if n < 1:
        n = 1
    if a == b:
        return {
            "fn": f, "label": FUNCTIONS[fn_key]["label"],
            "antideriv": FUNCTIONS[fn_key]["antideriv"],
            "dx": 0.0, "riemann": 0.0, "exact": 0.0, "error": 0.0, "bars": [],
            "a": a, "b": b, "n": n, "method": method,
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
        else:
            y = (f(x1) + f(x2)) / 2
        riemann += y * dx
        bars.append({"x1": x1, "x2": x2, "y": y, "method": method})
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
        "bars": bars, "a": a, "b": b, "n": n, "method": method,
    }


def _fmt(x, nd=3):
    s = f"{x:.{nd}f}"
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return s or "0"


def steps(fn_key, a, b, n, method, dx, riemann, exact, error, **_ignored):
    info = FUNCTIONS[fn_key]
    a_s, b_s, n_s = _fmt(a), _fmt(b), str(n)
    return [
        {"text": "Choose the integrand.",
         "formula": info["label"], "result": info["antideriv"]},
        {"text": "Split the interval [a, b] into n equal subintervals.",
         "formula": "Δx = (b − a) / n",
         "substitution": f"Δx = ({b_s} − {a_s}) / {n_s}",
         "result": f"Δx = {_fmt(dx, 4)}",
         "result_bind": ("b", float(b))},
        {"text": f"Apply the {method}-endpoint Riemann rule on each subinterval.",
         "formula": "R = Σ f(x*) · Δx",
         "substitution": f"sum over {n_s} rectangles, height = f(x*)",
         "result": f"R ≈ {_fmt(riemann, 4)}",
         "result_bind": ("n", float(n))},
        {"text": "The exact area is approximated with a high-resolution trapezoid.",
         "formula": "A = ∫[a,b] f(x) dx ≈ Σ (f(xᵢ)+f(xᵢ₊₁))/2 · Δx",
         "result": f"A ≈ {_fmt(exact, 4)}",
         "result_bind": ("b", float(b))},
        {"text": "Compare the two.",
         "formula": "error = R − A",
         "result": f"error ≈ {_fmt(error, 4)}",
         "result_bind": ("n", float(n))},
    ]


def solvers(params=None):
    """Parametric solvers — depend on the currently selected function and method."""
    fn_key = (params or {}).get("fn_key", "poly")
    method = (params or {}).get("method", "midpoint")
    info = FUNCTIONS.get(fn_key, FUNCTIONS["poly"])
    return {
        "vars": [
            {"symbol": "a", "label": "a",    "color": "#3b82f6"},
            {"symbol": "b", "label": "b",    "color": "#a855f7"},
            {"symbol": "n", "label": "n",    "color": "#f59e0b"},
            {"symbol": "A", "label": "area", "color": "#10b981"},
        ],
        "solvers": {
            "A": {"formula": f"A ≈ {method}-Riemann({info['label']})",
                  "compute_js": _riemann_js(info["fn_js"], method)},
        },
    }


def functions_meta():
    return [{"key": k, "label": v["label"], "antideriv": v["antideriv"]} for k, v in FUNCTIONS.items()]


def methods_meta():
    return [{"key": m, "label": m.capitalize()} for m in METHODS]
