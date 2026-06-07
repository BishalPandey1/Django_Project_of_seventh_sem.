"""Pure-Python math for the geometry module. 11 shapes. No Django imports."""

import math


def _circle(r, cx, cy):
    return {
        "shape": "circle",
        "cx": cx, "cy": cy, "r": r,
        "diameter": 2 * r,
        "circumference": 2 * math.pi * r,
        "area": math.pi * r * r,
    }


def _ellipse(rx, ry):
    if rx == 0 or ry == 0:
        return {"shape": "ellipse", "rx": rx, "ry": ry, "area": 0.0, "perimeter": 0.0,
                "c": 0.0, "e": 0.0}
    c = math.sqrt(abs(rx * rx - ry * ry))
    h = ((rx - ry) / (rx + ry)) ** 2
    p = math.pi * (rx + ry) * (1 + 3 * h / (10 + math.sqrt(4 - 3 * h)))
    a = math.pi * rx * ry
    e = c / max(rx, ry)
    return {"shape": "ellipse", "rx": rx, "ry": ry, "area": a, "perimeter": p, "c": c, "e": e}


def _square(s):
    return {"shape": "square", "s": s, "perimeter": 4 * s, "area": s * s, "diagonal": s * math.sqrt(2)}


def _rectangle(L, W):
    return {"shape": "rectangle", "L": L, "W": W,
            "perimeter": 2 * (L + W), "area": L * W, "diagonal": math.sqrt(L * L + W * W)}


def _triangle(Ax, Ay, Bx, By, Cx, Cy):
    a = math.hypot(Bx - Cx, By - Cy)
    b = math.hypot(Ax - Cx, Ay - Cy)
    c = math.hypot(Ax - Bx, Ay - By)
    perimeter = a + b + c
    s = perimeter / 2
    area_h = math.sqrt(max(0, s * (s - a) * (s - b) * (s - c)))
    area_s = 0.5 * abs(Ax * (By - Cy) + Bx * (Cy - Ay) + Cx * (Ay - By))

    def angle_at(opp, x, y):
        if x == 0 or y == 0:
            return 0.0
        return math.degrees(math.acos(max(-1, min(1, (x * x + y * y - opp * opp) / (2 * x * y)))))
    A = angle_at(a, b, c)
    B = angle_at(b, a, c)
    C = angle_at(c, a, b)
    return {"shape": "triangle", "vertices": [(Ax, Ay), (Bx, By), (Cx, Cy)],
            "sides": (a, b, c), "perimeter": perimeter,
            "area_heron": area_h, "area_shoelace": area_s, "area": area_h,
            "angles_deg": (A, B, C)}


def _right_triangle(a, b):
    c = math.hypot(a, b)
    area = 0.5 * a * b
    alpha = math.degrees(math.atan2(b, a)) if a != 0 else 90.0
    beta = math.degrees(math.atan2(a, b)) if b != 0 else 90.0
    return {"shape": "rightTriangle", "a": a, "b": b, "c": c, "area": area,
            "alpha": alpha, "beta": beta, "gamma": 90.0}


def _parallelogram(base, side, angle_deg):
    theta = math.radians(angle_deg)
    h = side * math.sin(theta)
    area = base * h
    perimeter = 2 * (base + side)
    d1_sq = base * base + side * side - 2 * base * side * math.cos(theta)
    d2_sq = base * base + side * side + 2 * base * side * math.cos(theta)
    return {"shape": "parallelogram", "base": base, "side": side, "angle_deg": angle_deg,
            "height": h, "area": area, "perimeter": perimeter,
            "diagonal1": math.sqrt(d1_sq), "diagonal2": math.sqrt(d2_sq)}


def _trapezoid(a, b, h):
    m = (a + b) / 2
    area = 0.5 * (a + b) * h
    leg = math.sqrt(((a - b) / 2) ** 2 + h * h)
    return {"shape": "trapezoid", "a": a, "b": b, "h": h,
            "midline": m, "area": area, "leg": leg, "perimeter": a + b + 2 * leg}


def _rhombus(p, q):
    s = math.sqrt((p / 2) ** 2 + (q / 2) ** 2)
    area = 0.5 * p * q
    theta = 2 * math.degrees(math.atan2(q, p)) if p != 0 else 90.0
    return {"shape": "rhombus", "p": p, "q": q, "side": s, "perimeter": 4 * s,
            "area": area, "angle_deg": theta}


def _sector(r, theta_deg):
    theta = math.radians(theta_deg)
    L = r * theta
    area = 0.5 * r * r * theta
    c = 2 * r * math.sin(theta / 2)
    return {"shape": "sector", "r": r, "theta_deg": theta_deg, "arc_length": L,
            "area": area, "chord": c, "perimeter": 2 * r + L}


def _polygon(n, r, rotation_deg):
    if n < 3:
        n = 3
    s = 2 * r * math.sin(math.pi / n)
    apothem = r * math.cos(math.pi / n)
    perimeter = n * s
    area = 0.5 * perimeter * apothem
    interior = (n - 2) * 180 / n
    exterior = 180 - interior
    rot = math.radians(rotation_deg)
    vertices = []
    for i in range(n):
        ang = rot + 2 * math.pi * i / n
        vertices.append((r * math.cos(ang), r * math.sin(ang)))
    return {"shape": "polygon", "n": n, "r": r, "rotation_deg": rotation_deg,
            "side": s, "apothem": apothem, "perimeter": perimeter, "area": area,
            "interior": interior, "exterior": exterior, "vertices": vertices}


SHAPES = ["circle", "ellipse", "square", "rectangle", "triangle", "rightTriangle",
          "parallelogram", "trapezoid", "rhombus", "sector", "polygon"]


PRESETS = [
    {"name": "Unit circle r=3",  "params": {"shape": "circle",  "r": 3, "cx": 0, "cy": 0},                  "blurb": "Centered at origin, radius 3."},
    {"name": "Off-center circle", "params": {"shape": "circle", "r": 4, "cx": 2, "cy": 1},                "blurb": "Translated circle."},
    {"name": "Tall ellipse",     "params": {"shape": "ellipse", "rx": 3, "ry": 6},                          "blurb": "Vertical major axis."},
    {"name": "Wide ellipse",     "params": {"shape": "ellipse", "rx": 7, "ry": 3},                          "blurb": "Horizontal major axis."},
    {"name": "Square s=5",       "params": {"shape": "square",  "s": 5},                                    "blurb": "Side length 5."},
    {"name": "3-4-5 triangle",   "params": {"shape": "rightTriangle", "a": 3, "b": 4},                     "blurb": "Classic right triangle."},
    {"name": "Equilateral",      "params": {"shape": "triangle", "Ax": -3, "Ay": -2, "Bx": 3, "By": -2, "Cx": 0, "Cy": 4.196}, "blurb": "All sides equal."},
    {"name": "Hexagon r=5",      "params": {"shape": "polygon", "n": 6, "r": 5, "rotation_deg": 0},         "blurb": "Regular hexagon."},
    {"name": "Pentagon r=5",     "params": {"shape": "polygon", "n": 5, "r": 5, "rotation_deg": 0},         "blurb": "Regular pentagon."},
    {"name": "60° sector r=4",   "params": {"shape": "sector", "r": 4, "theta_deg": 60},                   "blurb": "Pizza-slice."},
    {"name": "Golden rectangle", "params": {"shape": "rectangle", "L": 6.18, "W": 3.82},                   "blurb": "Aspect ratio φ."},
    {"name": "Rhombus p=6,q=4",  "params": {"shape": "rhombus", "p": 6, "q": 4},                            "blurb": "Two diagonals."},
    {"name": "Parallelogram",    "params": {"shape": "parallelogram", "base": 6, "side": 3, "angle_deg": 60}, "blurb": "Base 6, side 3, 60°."},
    {"name": "Isoceles trapezoid", "params": {"shape": "trapezoid", "a": 3, "b": 7, "h": 4},               "blurb": "Trapezoid with parallel top/bottom."},
]
BOUNDS  = {
    "r": (0.1, 15, 0.1), "cx": (-15, 15, 0.1), "cy": (-15, 15, 0.1),
    "rx": (0.1, 15, 0.1), "ry": (0.1, 15, 0.1),
    "s": (0.1, 15, 0.1),
    "L": (0.1, 15, 0.1), "W": (0.1, 15, 0.1),
    "Ax": (-15, 15, 0.1), "Ay": (-15, 15, 0.1),
    "Bx": (-15, 15, 0.1), "By": (-15, 15, 0.1),
    "Cx": (-15, 15, 0.1), "Cy": (-15, 15, 0.1),
    "a": (0.1, 15, 0.1), "b": (0.1, 15, 0.1),
    "base": (0.1, 15, 0.1), "side": (0.1, 15, 0.1), "angle_deg": (1, 170, 1),
    "h": (0.1, 15, 0.1), "p": (0.1, 15, 0.1), "q": (0.1, 15, 0.1),
    "theta_deg": (1, 359, 1),
    "n": (3, 20, 1), "r_polygon": (0.1, 15, 0.1), "rotation_deg": (0, 359, 1),
}


def _formula_geometry(**params):
    shape = params.get("shape", "circle")
    shape_keys = {entry[0] for entry in SHAPE_PARAMS.get(shape, [])}
    keys = [k for k in params
            if k in shape_keys and isinstance(params.get(k), (int, float))]
    parts = ", ".join(f"{k}={params[k]:g}" for k in keys)
    return f"{shape}({parts})" if parts else shape


def compute(shape, **params):
    if shape == "circle":
        return _circle(**params)
    if shape == "ellipse":
        return _ellipse(**params)
    if shape == "square":
        return _square(**params)
    if shape == "rectangle":
        return _rectangle(**params)
    if shape == "triangle":
        return _triangle(**params)
    if shape == "rightTriangle":
        return _right_triangle(**params)
    if shape == "parallelogram":
        return _parallelogram(**params)
    if shape == "trapezoid":
        return _trapezoid(**params)
    if shape == "rhombus":
        return _rhombus(**params)
    if shape == "sector":
        return _sector(**params)
    if shape == "polygon":
        return _polygon(**params)
    raise ValueError(f"Unknown shape: {shape}")


SHAPE_PARAMS = {
    "circle":        [("r",  "Radius",       3,  0.1,  15,  "#3b82f6"),
                      ("cx", "Center X",     0,  0.1,  15,  "#06b6d4"),
                      ("cy", "Center Y",     0,  0.1,  15,  "#a855f7")],
    "ellipse":       [("rx", "Semi-major",   5,  0.1,  15,  "#3b82f6"),
                      ("ry", "Semi-minor",   3,  0.1,  15,  "#a855f7")],
    "square":        [("s",  "Side",         4,  0.1,  15,  "#3b82f6")],
    "rectangle":     [("L",  "Length",       6,  0.1,  15,  "#3b82f6"),
                      ("W",  "Width",        4,  0.1,  15,  "#a855f7")],
    "triangle":      [("Ax", "A.x",         -3,  0.1,  15,  "#3b82f6"),
                      ("Ay", "A.y",         -2,  0.1,  15,  "#06b6d4"),
                      ("Bx", "B.x",          3,  0.1,  15,  "#a855f7"),
                      ("By", "B.y",         -2,  0.1,  15,  "#ec4899"),
                      ("Cx", "C.x",          0,  0.1,  15,  "#f97316"),
                      ("Cy", "C.y",          3,  0.1,  15,  "#10b981")],
    "rightTriangle": [("a",  "Leg a",        4,  0.1,  15,  "#3b82f6"),
                      ("b",  "Leg b",        3,  0.1,  15,  "#a855f7")],
    "parallelogram": [("base",         "Base",   5,  0.1, 15, "#3b82f6"),
                      ("side",         "Side",   3,  0.1, 15, "#a855f7"),
                      ("angle_deg",    "Angle°", 60, 1,  170, "#f59e0b")],
    "trapezoid":     [("a",  "Top a",        3,  0.1,  15,  "#3b82f6"),
                      ("b",  "Bottom b",     6,  0.1,  15,  "#a855f7"),
                      ("h",  "Height",       4,  0.1,  15,  "#10b981")],
    "rhombus":       [("p",  "Diagonal p",   6,  0.1,  15,  "#3b82f6"),
                      ("q",  "Diagonal q",   4,  0.1,  15,  "#a855f7")],
    "sector":        [("r",         "Radius",   5,  0.1, 15, "#3b82f6"),
                      ("theta_deg", "Angle°",   60, 1,  359, "#a855f7")],
    "polygon":       [("n",            "Sides n", 6,  1,  20, "#3b82f6"),
                      ("r",            "Circum-radius", 5, 0.1, 15, "#a855f7"),
                      ("rotation_deg", "Rotation°", 0, 1,  359, "#f59e0b")],
}


SHAPE_DEFAULTS = {
    "circle":        {"r": 3, "cx": 0, "cy": 0},
    "ellipse":       {"rx": 5, "ry": 3},
    "square":        {"s": 4},
    "rectangle":     {"L": 6, "W": 4},
    "triangle":      {"Ax": -3, "Ay": -2, "Bx": 3, "By": -2, "Cx": 0, "Cy": 3},
    "rightTriangle": {"a": 4, "b": 3},
    "parallelogram": {"base": 5, "side": 3, "angle_deg": 60},
    "trapezoid":     {"a": 3, "b": 6, "h": 4},
    "rhombus":       {"p": 6, "q": 4},
    "sector":        {"r": 5, "theta_deg": 60},
    "polygon":       {"n": 6, "r": 5, "rotation_deg": 0},
}


# ── per-shape area / perimeter formulas (JS-safe expressions) ──────────
# Use only the shape's own parameter names; the solver panel exposes the
# parameters of the currently selected shape as A/P-independent inputs.
SHAPE_AREA_JS = {
    "circle":        "Math.PI * r * r",
    "ellipse":       "Math.PI * rx * ry",
    "square":        "s * s",
    "rectangle":     "L * W",
    "triangle":      "Math.abs(Ax*(By-Cy) + Bx*(Cy-Ay) + Cx*(Ay-By)) / 2",
    "rightTriangle": "0.5 * a * b",
    "parallelogram": "base * side * Math.sin(angle_deg * Math.PI / 180)",
    "trapezoid":     "0.5 * (a + b) * h",
    "rhombus":       "0.5 * p * q",
    "sector":        "0.5 * r * r * (theta_deg * Math.PI / 180)",
    "polygon":       "0.5 * n * (2*r*Math.sin(Math.PI/n)) * (r*Math.cos(Math.PI/n))",
}

SHAPE_PERIMETER_JS = {
    "circle":        "2 * Math.PI * r",
    "ellipse":       ("Math.PI * (rx + ry) * "
                      "(1 + 3 * Math.pow((rx-ry)/(rx+ry), 2) / "
                      "(10 + Math.sqrt(4 - 3 * Math.pow((rx-ry)/(rx+ry), 2))))"),
    "square":        "4 * s",
    "rectangle":     "2 * (L + W)",
    "triangle":      ("Math.hypot(Bx-Cx, By-Cy) + "
                      "Math.hypot(Ax-Cx, Ay-Cy) + "
                      "Math.hypot(Ax-Bx, Ay-By)"),
    "rightTriangle": "a + b + Math.hypot(a, b)",
    "parallelogram": "2 * (base + side)",
    "trapezoid":     ("a + b + 2 * Math.sqrt(Math.pow((a-b)/2, 2) + h*h)"),
    "rhombus":       ("4 * Math.sqrt(Math.pow(p/2, 2) + Math.pow(q/2, 2))"),
    "sector":        "2 * r + r * (theta_deg * Math.PI / 180)",
    "polygon":       "n * 2 * r * Math.sin(Math.PI / n)",
}


def steps(shape, **params_and_computed):
    if shape == "circle":
        r, cx, cy = params_and_computed["r"], params_and_computed["cx"], params_and_computed["cy"]
        d = 2 * r; C = 2 * math.pi * r; A = math.pi * r * r
        return [
            {"text": "A circle is the set of points at a fixed distance from a center.",
             "formula": "C(r) = {(x,y) : (x−cx)² + (y−cy)² = r²}",
             "result": "circle equation"},
            {"text": "Diameter is twice the radius.",
             "formula": "d = 2r", "substitution": f"d = 2·{r}", "result": f"d = {d:.3f}",
             "result_bind": ("r", float(r))},
            {"text": "Circumference (perimeter).",
             "formula": "C = 2πr", "substitution": f"C = 2π·{r}", "result": f"C = {C:.3f}",
             "result_bind": ("r", float(r))},
            {"text": "Area enclosed by the circle.",
             "formula": "A = πr²", "substitution": f"A = π·{r}²", "result": f"A = {A:.3f}",
             "result_bind": ("r", float(r))},
        ]
    if shape == "ellipse":
        rx, ry = params_and_computed["rx"], params_and_computed["ry"]
        c = math.sqrt(abs(rx * rx - ry * ry))
        e = c / max(rx, ry) if max(rx, ry) else 0
        a = math.pi * rx * ry
        return [
            {"text": "An ellipse is the set of points whose sum of distances to the foci is constant.",
             "formula": "(x/rx)² + (y/ry)² = 1",
             "result": "ellipse equation"},
            {"text": "Area is π times the product of the two semi-axes.",
             "formula": "A = π·rx·ry", "result": f"A = {a:.3f}",
             "result_bind": ("rx", float(rx))},
            {"text": "Linear eccentricity c is the distance from the center to each focus.",
             "formula": "c = √|rx² − ry²|", "result": f"c = {c:.3f}",
             "result_bind": ("rx", float(rx))},
            {"text": "Eccentricity measures the 'flatness' of the ellipse.",
             "formula": "e = c / max(rx, ry)", "result": f"e = {e:.3f}",
             "result_bind": ("rx", float(rx))},
        ]
    if shape == "square":
        s = params_and_computed["s"]
        return [
            {"text": "A square has four equal sides and four right angles.",
             "formula": "P = 4s", "result": f"P = {4*s:.3f}",
             "result_bind": ("s", float(s))},
            {"text": "Area is side squared.",
             "formula": "A = s²", "result": f"A = {s*s:.3f}",
             "result_bind": ("s", float(s))},
            {"text": "Diagonal length via Pythagoras.",
             "formula": "d = s√2", "result": f"d = {s*math.sqrt(2):.3f}",
             "result_bind": ("s", float(s))},
        ]
    if shape == "rectangle":
        L, W = params_and_computed["L"], params_and_computed["W"]
        return [
            {"text": "A rectangle has two pairs of equal sides and four right angles.",
             "formula": "P = 2(L + W)", "result": f"P = {2*(L+W):.3f}",
             "result_bind": ("L", float(L))},
            {"text": "Area is the product of the two sides.",
             "formula": "A = L·W", "result": f"A = {L*W:.3f}",
             "result_bind": ("L", float(L))},
            {"text": "Diagonal via Pythagoras.",
             "formula": "d = √(L² + W²)", "result": f"d = {math.sqrt(L*L+W*W):.3f}",
             "result_bind": ("L", float(L))},
        ]
    if shape == "triangle":
        Ax, Ay = params_and_computed["Ax"], params_and_computed["Ay"]
        Bx, By = params_and_computed["Bx"], params_and_computed["By"]
        Cx, Cy = params_and_computed["Cx"], params_and_computed["Cy"]
        a = math.hypot(Bx-Cx, By-Cy)
        b = math.hypot(Ax-Cx, Ay-Cy)
        c = math.hypot(Ax-Bx, Ay-By)
        s = (a+b+c)/2
        area = math.sqrt(max(0, s*(s-a)*(s-b)*(s-c)))
        return [
            {"text": "The side lengths are pairwise distances between the vertices.",
             "formula": "a = ‖B−C‖,  b = ‖A−C‖,  c = ‖A−B‖",
             "result": f"a = {a:.3f},  b = {b:.3f},  c = {c:.3f}"},
            {"text": "Perimeter is the sum of the three sides.",
             "formula": "P = a + b + c", "result": f"P = {a+b+c:.3f}"},
            {"text": "Use Heron's formula to find the area.",
             "formula": "A = √(s(s−a)(s−b)(s−c))", "result": f"A = {area:.3f}"},
            {"text": "Interior angles via the law of cosines.",
             "formula": "A = arccos((b²+c²−a²)/(2bc))",
             "result": f"α = {params_and_computed.get('angles_deg',(0,0,0))[0]:.2f}°"},
        ]
    if shape == "rightTriangle":
        a, b = params_and_computed["a"], params_and_computed["b"]
        c = math.hypot(a, b)
        return [
            {"text": "The hypotenuse is opposite the right angle.",
             "formula": "c = √(a² + b²)", "result": f"c = {c:.3f}",
             "result_bind": ("a", float(a))},
            {"text": "Area is half the product of the legs.",
             "formula": "A = ½·a·b", "result": f"A = {0.5*a*b:.3f}",
             "result_bind": ("a", float(a))},
            {"text": "Acute angles from inverse tangent.",
             "formula": "α = atan(b/a),  β = atan(a/b)",
             "result": f"α = {math.degrees(math.atan2(b,a)):.2f}°,  β = {math.degrees(math.atan2(a,b)):.2f}°"},
        ]
    if shape == "parallelogram":
        base, side, ang = (params_and_computed["base"], params_and_computed["side"],
                           params_and_computed["angle_deg"])
        h = side * math.sin(math.radians(ang))
        return [
            {"text": "Height is the perpendicular distance between the two bases.",
             "formula": "h = side·sin(θ)", "result": f"h = {h:.3f}",
             "result_bind": ("side", float(side))},
            {"text": "Area is base times height.",
             "formula": "A = base·h", "result": f"A = {base*h:.3f}",
             "result_bind": ("base", float(base))},
            {"text": "Perimeter is twice the sum of adjacent sides.",
             "formula": "P = 2(base + side)", "result": f"P = {2*(base+side):.3f}",
             "result_bind": ("base", float(base))},
        ]
    if shape == "trapezoid":
        a, b, h = params_and_computed["a"], params_and_computed["b"], params_and_computed["h"]
        return [
            {"text": "The midline is the average of the two parallel sides.",
             "formula": "m = (a + b) / 2", "result": f"m = {(a+b)/2:.3f}",
             "result_bind": ("a", float(a))},
            {"text": "Area is midline times height.",
             "formula": "A = m·h", "result": f"A = {0.5*(a+b)*h:.3f}",
             "result_bind": ("h", float(h))},
            {"text": "Each leg follows Pythagoras from the height and the horizontal offset.",
             "formula": "leg = √(((a−b)/2)² + h²)",
             "result": f"leg = {math.sqrt(((a-b)/2)**2 + h*h):.3f}",
             "result_bind": ("h", float(h))},
        ]
    if shape == "rhombus":
        p, q = params_and_computed["p"], params_and_computed["q"]
        s = math.sqrt((p/2)**2 + (q/2)**2)
        return [
            {"text": "The side length follows from the half-diagonals (Pythagoras).",
             "formula": "s = √((p/2)² + (q/2)²)", "result": f"s = {s:.3f}",
             "result_bind": ("p", float(p))},
            {"text": "Perimeter is four times the side length.",
             "formula": "P = 4s", "result": f"P = {4*s:.3f}",
             "result_bind": ("p", float(p))},
            {"text": "Area is half the product of the diagonals.",
             "formula": "A = ½·p·q", "result": f"A = {0.5*p*q:.3f}",
             "result_bind": ("p", float(p))},
        ]
    if shape == "sector":
        r, theta = params_and_computed["r"], params_and_computed["theta_deg"]
        t = math.radians(theta)
        return [
            {"text": "Arc length is the radius times the angle (in radians).",
             "formula": "L = r·θ", "result": f"L = {r*t:.3f}",
             "result_bind": ("r", float(r))},
            {"text": "Sector area is half the radius squared times the angle.",
             "formula": "A = ½·r²·θ", "result": f"A = {0.5*r*r*t:.3f}",
             "result_bind": ("r", float(r))},
            {"text": "The chord (straight line between endpoints).",
             "formula": "c = 2r·sin(θ/2)", "result": f"c = {2*r*math.sin(t/2):.3f}",
             "result_bind": ("r", float(r))},
        ]
    if shape == "polygon":
        n, r = params_and_computed["n"], params_and_computed["r"]
        s = 2 * r * math.sin(math.pi / n)
        a = r * math.cos(math.pi / n)
        return [
            {"text": "Each side spans 2π/n of the circumscribed circle.",
             "formula": "s = 2r·sin(π/n)", "result": f"s = {s:.3f}",
             "result_bind": ("n", int(n))},
            {"text": "The apothem is the distance from the center to a side.",
             "formula": "a = r·cos(π/n)", "result": f"a = {a:.3f}",
             "result_bind": ("n", int(n))},
            {"text": "Perimeter and area.",
             "formula": "P = n·s,  A = ½·P·a",
             "result": f"P = {n*s:.3f},  A = {0.5*n*s*a:.3f}",
             "result_bind": ("r", float(r))},
            {"text": "Interior / exterior angle.",
             "formula": "(n−2)·180/n ,  180 − that",
             "result": f"{180 - 180/n:.2f}° / {180/n:.2f}°"},
        ]
    return []


def solvers(params=None):
    """Parametric solvers — compute area & perimeter for the current shape.

    The user can override the per-shape parameter values from the solver
    panel (any param that isn't A/P is exposed as a free input). The
    ``compute_js`` expressions are the per-shape formulas above, looked up
    by the currently selected ``shape``.
    """
    shape = (params or {}).get("shape", "circle")
    area_js = SHAPE_AREA_JS.get(shape, "0")
    perim_js = SHAPE_PERIMETER_JS.get(shape, "0")
    return {
        "vars": [
            {"symbol": "A", "label": "Area",   "color": "#3b82f6"},
            {"symbol": "P", "label": "Perim.", "color": "#a855f7"},
        ],
        "solvers": {
            "A": {"formula": f"A({shape})", "compute_js": area_js},
            "P": {"formula": f"P({shape})", "compute_js": perim_js},
        },
    }


FORMULA = _formula_geometry
