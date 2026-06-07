"""Seed the reading room with 7 full articles (no lorem ipsum)."""

from django.core.management.base import BaseCommand

from apps.reading.models import ReadingPage


PAGES = [
    ("linear", "Linear Functions", """
# Linear Functions

## Definition
A linear function is a mapping of the form y = m·x + b. Its graph is a straight
line with slope m and y-intercept b. Linear functions are the simplest
relationship between two quantities: doubling the input doubles the output
when b = 0.

## Formulas
- **Slope–intercept form:** y = m·x + b
- **Point–slope form:** y − y₁ = m·(x − x₁)
- **Standard form:** A·x + B·y = C
- **Slope:** m = (y₂ − y₁) / (x₂ − x₁)
- **x-intercept:** −b / m
- **Angle with x-axis:** θ = arctan(m)

## Worked Example
Given y = 2·x + 1:
- m = 2, b = 1
- y-intercept: (0, 1)
- x-intercept: −1/2 = −0.5
- angle: arctan(2) ≈ 63.43°

## Common Pitfalls
- A horizontal line (m = 0) has no x-intercept.
- A vertical line is **not** a function and cannot be written in y = m·x + b.
- Forgetting that "parallel" lines have equal slopes, not equal intercepts.
"""),
    ("quadratic", "Quadratics", """
# Quadratics

## Definition
A quadratic function has the form y = a·x² + b·x + c with a ≠ 0. Its graph is
a parabola — a U-shape that opens up when a > 0 and down when a < 0.

## Formulas
- **Vertex:** x_v = −b / (2a),  y_v = a·x_v² + b·x_v + c
- **Discriminant:** Δ = b² − 4ac
  - Δ > 0: two real roots
  - Δ = 0: one repeated root
  - Δ < 0: no real roots
- **Roots:** x = (−b ± √Δ) / (2a)
- **Axis of symmetry:** x = −b / (2a)
- **Standard to vertex:** a·(x − h)² + k

## Worked Example
y = x² − 4x + 3:
- a = 1, b = −4, c = 3
- Vertex: x_v = 2, y_v = −1
- Δ = 16 − 12 = 4
- Roots: (4 ± 2) / 2 = 1, 3

## Common Pitfalls
- Sign of b is the **opposite** of the vertex's x in some problems — be careful.
- If a < 0 the vertex is a **maximum**, not a minimum.
- Double roots touch the x-axis; they don't cross it.
"""),
    ("trig", "Sine Waves", """
# Sine Waves

## Definition
A sine wave is any function of the form y = A·sin(B·x + C) + D. The
parameters control the amplitude, period, phase shift, and midline.

## Formulas
- **Amplitude:** |A|
- **Period:** T = 2π / |B|
- **Phase shift:** −C / B
- **Midline:** y = D
- **Frequency:** 1 / T
- **Angular frequency:** B (radians per unit x)

## Worked Example
y = 3·sin(2·x) + 1:
- A = 3, B = 2, C = 0, D = 1
- Amplitude 3, period π, midline y = 1
- The curve oscillates between y = −2 and y = 4.

## Common Pitfalls
- A larger |B| means a **shorter** period (curve compresses horizontally).
- Cosine is just sine shifted by π/2: cos(x) = sin(x + π/2).
- Phase shifts move the curve **horizontally**, not vertically.
"""),
    ("derivative", "Derivatives", """
# Derivatives

## Definition
The derivative f′(x) of a function f at a point x is the instantaneous rate
of change — geometrically, the slope of the tangent line. The limit definition
uses a difference quotient.

## Formulas
- **Limit definition:** f′(x) = lim[h→0] (f(x+h) − f(x)) / h
- **Power rule:** d/dx[xⁿ] = n·xⁿ⁻¹
- **Sum rule:** d/dx[f + g] = f′ + g′
- **Product rule:** (f·g)′ = f′·g + f·g′
- **Chain rule:** d/dx[f(g(x))] = f′(g(x))·g′(x)
- **Trig:** d/dx[sin x] = cos x, d/dx[cos x] = −sin x

## Worked Example
For f(x) = x² at x₀ = 3:
- f′(x) = 2x
- f′(3) = 6
- Tangent line: y = 6·(x − 3) + 9

## Common Pitfalls
- The derivative is a **function**, not a number — at each x it gives a slope.
- The secant line's slope approximates the tangent's; the error shrinks as h → 0.
- d/dx[1/x] = −1/x², not +1/x².
"""),
    ("integral", "Integrals", """
# Integrals

## Definition
The definite integral ∫[a, b] f(x) dx is the signed area under the curve
f(x) from x = a to x = b. Riemann sums approximate the integral with
rectangles; finer n means better accuracy.

## Formulas
- **Left Riemann:** Σᵢ f(xᵢ)·Δx
- **Right Riemann:** Σᵢ f(xᵢ₊₁)·Δx
- **Midpoint:** Σᵢ f((xᵢ + xᵢ₊₁)/2)·Δx
- **Trapezoid:** Σᵢ (f(xᵢ) + f(xᵢ₊₁))/2 · Δx
- **Fundamental theorem:** ∫[a, b] f = F(b) − F(a)
- **Antiderivatives:** ∫xⁿ dx = xⁿ⁺¹/(n+1) + C

## Worked Example
∫[0, 4] x²/4 dx with n = 4:
- Δx = 1
- Midpoint rule: f(0.5) + f(1.5) + f(2.5) + f(3.5) ≈ 0.0625 + 0.5625 + 1.5625 + 3.0625 = 5.25
- Exact: F(4) − F(0) = 64/12 = 5.333...

## Common Pitfalls
- ∫f dx returns a **family** of functions; ∫[a,b] f dx returns a **number**.
- Reimann sums can over- or under-shoot the true area depending on monotonicity.
- Don't forget the absolute value when integrating 1/x — it is ln|x| + C.
"""),
    ("geometry", "Geometry", """
# Geometry

## Definition
Geometry studies the **shapes** and their **measurements**. Each shape has
its own formulas for perimeter, area, and key lengths.

## Formulas (selected)
- **Circle:** C = 2πr, A = πr²
- **Triangle (Heron):** A = √(s(s−a)(s−b)(s−c))  with s = (a+b+c)/2
- **Right triangle:** c = √(a² + b²), A = ½ab
- **Rhombus:** A = ½·p·q  (p, q = diagonals)
- **Regular n-gon:** A = ½·n·s·a  (a = apothem)
- **Interior angle:** (n − 2)·180 / n

## Worked Example
A right triangle with legs 3 and 4:
- Hypotenuse: 5
- Area: ½·3·4 = 6
- Angles: arctan(4/3) ≈ 53.13° and arctan(3/4) ≈ 36.87°

## Common Pitfalls
- Don't confuse "radius" (circle) with "diameter" — diameter = 2·radius.
- Heron's formula needs the **three sides**, not coordinates.
- The "shoelace formula" and Heron's formula can disagree for **degenerate**
  (collinear) triangles — check the orientation.
"""),
    ("transform", "Linear Transforms", """
# Linear Transforms

## Definition
A 2×2 matrix M = [[a, b], [c, d]] acts on the plane by sending (x, y) to
(a·x + b·y, c·x + d·y). The columns of M are the images of the standard
basis vectors î and ĵ.

## Formulas
- **Apply:** M·(x, y) = (a·x + b·y, c·x + d·y)
- **Determinant:** det(M) = a·d − b·c
- **Inverse:** (1/det)·[[d, −b], [−c, a]]  (when det ≠ 0)
- **Rotation by θ:** [[cos θ, −sin θ], [sin θ, cos θ]]
- **Scale by k:** [[k, 0], [0, k]]
- **Shear:** [[1, k], [0, 1]]

## Worked Example
M = [[0, −1], [1, 0]] rotates by 90°:
- (1, 0) → (0, 1)
- (0, 1) → (−1, 0)
- det = 0·0 − (−1)·1 = 1, so area is preserved and orientation is preserved.

## Common Pitfalls
- det(M) = 0 means M is **singular** — it collapses the plane to a line.
- Composition M·N is **not** commutative; order matters.
- "Flip" transforms have negative determinants; rotations and scales have positive ones.
"""),
]


class Command(BaseCommand):
    help = "Create 7 reading-room articles (idempotent)."

    def handle(self, *args, **options):
        for order, (slug, title, body) in enumerate(PAGES):
            obj, created = ReadingPage.objects.update_or_create(
                slug=slug,
                defaults={
                    "module_id": slug,
                    "title": title,
                    "body_md": body.strip(),
                    "order": order,
                },
            )
            self.stdout.write(("Created" if created else "Updated") + f" {slug}")
        self.stdout.write(self.style.SUCCESS(f"Done — {len(PAGES)} reading pages in DB."))
