"""Pure-Python math for the linear-transforms module. No Django imports."""


PRESETS = [
    {"name": "Identity",   "a": 1,  "b": 0, "c": 0, "d": 1},
    {"name": "Rotate 90°", "a": 0,  "b": -1, "c": 1, "d": 0},
    {"name": "Scale ×2",   "a": 2,  "b": 0, "c": 0, "d": 2},
    {"name": "Shear",      "a": 1,  "b": 1, "c": 0, "d": 1},
    {"name": "Flip x",     "a": -1, "b": 0, "c": 0, "d": 1},
    {"name": "Flip y",     "a": 1,  "b": 0, "c": 0, "d": -1},
]


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
        "a": a, "b": b, "c": c, "d": d,
    }


def steps(a, b, c, d, det, i_hat, j_hat, singular, orientation, **_ignored):
    s = [
        {"text": "A 2×2 matrix transforms the plane linearly.",
         "formula": "[a b; c d]·[x; y] = [a·x + b·y; c·x + d·y]"},
        {"text": "Substitute the current matrix entries.",
         "substitution": f"[{a:.2f} {b:.2f}; {c:.2f} {d:.2f}]"},
        {"text": "Image of the basis vector î = (1, 0).",
         "formula": "M·(1,0) = (a, c)",
         "result": f"M·î = ({i_hat[0]:.3f}, {i_hat[1]:.3f})",
         "result_bind": ("a", float(a))},
        {"text": "Image of the basis vector ĵ = (0, 1).",
         "formula": "M·(0,1) = (b, d)",
         "result": f"M·ĵ = ({j_hat[0]:.3f}, {j_hat[1]:.3f})",
         "result_bind": ("d", float(d))},
        {"text": "The determinant gives area scale and orientation.",
         "formula": "det = a·d − b·c",
         "substitution": f"det = {a:.2f}·{d:.2f} − {b:.2f}·{c:.2f}",
         "result": f"det = {det:.4f}"},
        {"text": f"Orientation is {orientation} (det sign).",
         "formula": "det > 0: preserved,  det < 0: flipped",
         "result": "singular" if singular else "invertible"},
    ]
    return s


def solvers():
    return {
        "vars": [
            {"symbol": "a", "label": "a", "color": "#3b82f6"},
            {"symbol": "b", "label": "b", "color": "#a855f7"},
            {"symbol": "c", "label": "c", "color": "#f59e0b"},
            {"symbol": "d", "label": "d", "color": "#10b981"},
        ],
        "solvers": {
            "a": {"formula": "a", "compute_js": "a"},
            "b": {"formula": "b", "compute_js": "b"},
            "c": {"formula": "c", "compute_js": "c"},
            "d": {"formula": "d", "compute_js": "d"},
        },
    }
