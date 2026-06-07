"""Pure-Python math for the linear-transforms module. No Django imports."""


PRESETS = [
    {"name": "Identity",   "params": {"a": 1,  "b": 0,  "c": 0, "d": 1},  "blurb": "Leaves the plane unchanged."},
    {"name": "Rotate 90°", "params": {"a": 0,  "b": -1, "c": 1, "d": 0},  "blurb": "Quarter turn about the origin."},
    {"name": "Scale ×2",   "params": {"a": 2,  "b": 0,  "c": 0, "d": 2},  "blurb": "Doubles both axes."},
    {"name": "Shear",      "params": {"a": 1,  "b": 1,  "c": 0, "d": 1},  "blurb": "Slants the unit square."},
    {"name": "Flip x",     "params": {"a": -1, "b": 0,  "c": 0, "d": 1},  "blurb": "Mirror across the y-axis."},
    {"name": "Flip y",     "params": {"a": 1,  "b": 0,  "c": 0, "d": -1}, "blurb": "Mirror across the x-axis."},
]
BOUNDS  = {"a": (-5, 5, 0.05), "b": (-5, 5, 0.05), "c": (-5, 5, 0.05), "d": (-5, 5, 0.05)}
FORMULA = lambda a, b, c, d, **_kw: f"M = [{a:.3f}  {b:.3f}; {c:.3f}  {d:.3f}]"


def compute(a, b, c, d):
    original = [(1, 0), (2, 0), (2, 1), (3, 1), (3, 2), (1, 2)]
    transformed = [(a * x + b * y, c * x + d * y) for x, y in original]
    det = a * d - b * c
    return {
        "original": original,
        "transformed": transformed,
        "det": det,
        "i_hat": (a, c),
        "j_hat": (b, d),
        "singular": abs(det) < 1e-6,
        "orientation": "preserved" if det >= 0 else "flipped",
        "trace": a + d,
        "a": a, "b": b, "c": c, "d": d,
    }


def _fmt(x, nd=3):
    s = f"{x:.{nd}f}"
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return s or "0"


def steps(a, b, c, d, det, i_hat, j_hat, singular, orientation, trace, **_ignored):
    a_s, b_s, c_s, d_s = _fmt(a), _fmt(b), _fmt(c), _fmt(d)
    s = [
        {"text": "A 2×2 matrix transforms the plane linearly.",
         "formula": "[a b; c d]·[x; y] = [a·x + b·y; c·x + d·y]",
         "result": "[a b; c d]·[x; y] = [a·x + b·y; c·x + d·y]"},
        {"text": "Substitute the current matrix entries.",
         "substitution": f"[{a_s} {b_s}; {c_s} {d_s}]",
         "result": f"M = [{a_s} {b_s}; {c_s} {d_s}]",
         "result_bind": ("a", float(a))},
        {"text": "Image of the basis vector î = (1, 0).",
         "formula": "M·(1,0) = (a, c)",
         "substitution": f"M·(1, 0) = ({a_s}, {c_s})",
         "result": f"M·î = ({_fmt(i_hat[0])}, {_fmt(i_hat[1])})",
         "result_bind": ("a", float(a))},
        {"text": "Image of the basis vector ĵ = (0, 1).",
         "formula": "M·(0,1) = (b, d)",
         "substitution": f"M·(0, 1) = ({b_s}, {d_s})",
         "result": f"M·ĵ = ({_fmt(j_hat[0])}, {_fmt(j_hat[1])})",
         "result_bind": ("d", float(d))},
        {"text": "Determinant gives area scale and orientation.",
         "formula": "det = a·d − b·c",
         "substitution": f"det = {a_s}·{d_s} − {b_s}·{c_s}",
         "result": f"det = {_fmt(det, 4)}",
         "result_bind": ("a", float(a))},
        {"text": "Trace is the sum of the diagonal entries (related to eigenvalues).",
         "formula": "trace = a + d",
         "substitution": f"trace = {a_s} + {d_s}",
         "result": f"trace = {_fmt(trace)}",
         "result_bind": ("a", float(a))},
        {"text": f"Orientation is {orientation} (sign of det).",
         "formula": "det > 0: preserved,  det < 0: flipped",
         "result": "singular (no inverse)" if singular else "invertible"},
    ]
    return s


def solvers(_params=None):
    """Solve for any of the six transform quantities given the other five.

    The solver panel exposes six vars: the four matrix entries a, b, c, d
    and the two output components u, v (for an input point (x, y)). The
    ``compute_js`` expressions are picked so the user can type in the five
    knowns and read off the target.
    """
    return {
        "vars": [
            {"symbol": "a", "label": "a",    "color": "#3b82f6"},
            {"symbol": "b", "label": "b",    "color": "#a855f7"},
            {"symbol": "c", "label": "c",    "color": "#f59e0b"},
            {"symbol": "d", "label": "d",    "color": "#10b981"},
            {"symbol": "u", "label": "u = ax+by", "color": "#06b6d4"},
            {"symbol": "v", "label": "v = cx+dy", "color": "#ec4899"},
            {"symbol": "x", "label": "x",    "color": "#84cc16"},
            {"symbol": "y", "label": "y",    "color": "#f43f5e"},
        ],
        "solvers": {
            "u": {"formula": "u = a·x + b·y",
                  "compute_js": "a*x + b*y"},
            "v": {"formula": "v = c·x + d·y",
                  "compute_js": "c*x + d*y"},
            "a": {"formula": "a = (u − b·y) / x   (if x ≠ 0)",
                  "compute_js": "(u - b*y) / x"},
            "b": {"formula": "b = (u − a·x) / y   (if y ≠ 0)",
                  "compute_js": "(u - a*x) / y"},
            "c": {"formula": "c = (v − d·y) / x   (if x ≠ 0)",
                  "compute_js": "(v - d*y) / x"},
            "d": {"formula": "d = (v − c·x) / y   (if y ≠ 0)",
                  "compute_js": "(v - c*x) / y"},
        },
    }
