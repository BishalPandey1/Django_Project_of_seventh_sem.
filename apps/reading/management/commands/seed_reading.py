"""Seed the reading room with 7 full, book-quality chapters.

Each chapter includes: an origin/history, the core definition, a long list of
key formulas, multiple worked examples, key ideas to remember, real-world
applications, and common pitfalls — so a reader gets a real "book" feel.
"""

from django.core.management.base import BaseCommand

from apps.reading.models import ReadingPage


PAGES = [

    # ─── Chapter 1 — Linear Functions ─────────────────────────────────
    ("linear", "Linear Functions", r"""
# Linear Functions

## Origin and a little history
The idea of a straight-line relationship goes back to the Babylonians
(~1900 BCE), who used linear interpolation to predict planetary
positions. The Greek mathematicians Euclid and Apollonius studied
proportional reasoning; Descartes and Fermat turned it into analytic
geometry in the 1630s by pairing an equation with a graph. The slope
notation `m` is believed to come from the French *monter* — "to rise".

## Definition
A **linear function** is a mapping of the form `y = m·x + b`. Its graph
is a straight line in the Cartesian plane with slope `m` and `y`-intercept
`b`. Linear functions are the simplest relationship between two
quantities — doubling the input doubles the output when `b = 0`, and
adding a fixed offset shifts the entire line up or down.

Geometrically, `m` controls *direction* and *steepness*; `b` controls
*position*. The line is monotonic: it is strictly increasing when
`m > 0`, strictly decreasing when `m < 0`, and constant when `m = 0`.

## Key formulas
- **Slope–intercept form:** `y = m·x + b`
- **Point–slope form:** `y − y₁ = m·(x − x₁)`
- **Two-point form:** `m = (y₂ − y₁) / (x₂ − x₁)`
- **Standard form:** `A·x + B·y = C`
- **x-intercept (root):** `x = −b / m`  (when `m ≠ 0`)
- **y-intercept:** `y = b`
- **Angle with the x-axis:** `θ = arctan(m)`
- **Distance between two points:** `√((x₂−x₁)² + (y₂−y₁)²)`
- **Midpoint of two points:** `((x₁+x₂)/2,  (y₁+y₂)/2)`
- **Parallel lines:** `m₁ = m₂`
- **Perpendicular lines:** `m₁ · m₂ = −1`

## Worked example 1 — identifying a line
For `y = 2·x + 1`:

| quantity | value |
|---|---|
| slope `m` | 2 |
| intercept `b` | 1 |
| y-intercept | (0, 1) |
| x-intercept | (−½, 0) |
| angle θ | arctan(2) ≈ 63.43° |

A horizontal change of 1 unit moves the line up by `m = 2` units. A
vertical change of 5 units corresponds to a horizontal change of
`Δx = 5 / m = 2.5` units.

## Worked example 2 — line through two points
Find the line through `P = (1, 4)` and `Q = (5, 12)`:

1. Slope: `m = (12 − 4) / (5 − 1) = 8 / 4 = 2`
2. Point–slope form: `y − 4 = 2·(x − 1)`
3. Simplify: `y = 2·x + 2`

Verification: at `x = 5`, `y = 2·5 + 2 = 12` — matches point `Q`.

## Worked example 3 — perpendicular line
The line `y = 3·x − 1` has slope `m₁ = 3`. A line perpendicular to it
through `(0, 4)`:

1. Perpendicular slope: `m₂ = −1 / m₁ = −1 / 3`
2. Through `(0, 4)`: `y = −(1/3)·x + 4`

The product `m₁ · m₂ = 3 · (−1/3) = −1` — exactly as required.

## Real-world applications
- **Economics:** cost = fixed cost + variable cost · quantity, a
  straight line through the origin plus an offset.
- **Physics:** at constant velocity, position vs. time is linear.
- **Engineering:** Ohm's law `V = I·R` is a linear relationship
  between voltage and current.
- **Conversion:** temperature scales `F = (9/5)·C + 32` translate
  Celsius to Fahrenheit.

## Key ideas to remember
- Two lines are **parallel** iff their slopes are equal.
- Two lines are **perpendicular** iff `m₁ · m₂ = −1`.
- A line through the origin always has `b = 0` and is a direct
  proportion.
- A vertical line is **not** a function and cannot be written
  `y = m·x + b`.

## Common pitfalls
- A horizontal line (`m = 0`) has no x-intercept.
- Forgetting that "parallel" lines share slopes, **not** intercepts.
- Mixing up *interpolation* (predicting inside the data range) with
  *extrapolation* (predicting outside it) — only the former is reliable.
- Sign errors when moving terms across the equals sign.
"""),

    # ─── Chapter 2 — Quadratics ──────────────────────────────────────
    ("quadratic", "Quadratics", r"""
# Quadratics

## Origin and a little history
Quadratic equations were already being solved in ancient Babylon
(around 2000 BCE) by a recipe that looks surprisingly like the modern
quadratic formula. Indian mathematicians (Brahmagupta, 7th century) and
Persian mathematicians (al-Khwarizmi, 9th century) wrote the first
algebraic treatments. The word "quadratic" comes from the Latin
*quadratus*, meaning "square" — because the unknown is raised to the
second power.

## Definition
A **quadratic function** has the form `y = a·x² + b·x + c` with `a ≠ 0`.
Its graph is a **parabola** — a symmetric U-shape that opens upward
when `a > 0` and downward when `a < 0`. The parabola has a single
turning point, the **vertex**, which is the minimum (or maximum) value
of the function.

Quadratics model the motion of projectiles under gravity, the area of
a rectangle with a fixed perimeter, and the shape of satellite dishes
and telescope mirrors.

## Key formulas
- **Vertex:** `x_v = −b / (2a)`,   `y_v = a·x_v² + b·x_v + c`
- **Axis of symmetry:** `x = −b / (2a)`
- **Discriminant:** `Δ = b² − 4ac`
  - `Δ > 0` → two distinct real roots
  - `Δ = 0` → one repeated real root
  - `Δ < 0` → no real roots (complex conjugates)
- **Roots (quadratic formula):** `x = (−b ± √Δ) / (2a)`
- **Vertex form:** `y = a·(x − h)² + k`, with vertex at `(h, k)`
- **Factored form:** `y = a·(x − r₁)·(x − r₂)`
- **Sum / product of roots:** `r₁ + r₂ = −b / a`,   `r₁ · r₂ = c / a`
- **Minimum / maximum value:** `y_v` at the vertex

## Worked example 1 — find roots
Solve `x² − 4x + 3 = 0`:

| quantity | value |
|---|---|
| `a, b, c` | 1, −4, 3 |
| discriminant | 16 − 12 = 4 |
| roots | `(4 ± 2) / 2 = 1, 3` |
| vertex | (2, −1) |
| axis of symmetry | x = 2 |

The parabola opens upward, dips to `(2, −1)`, and crosses the x-axis
at `x = 1` and `x = 3`.

## Worked example 2 — repeated root
Solve `x² − 6x + 9 = 0`:

- Discriminant: `Δ = 36 − 36 = 0`
- Root: `x = 6 / 2 = 3` (a *double* root)
- The parabola just touches the x-axis at `(3, 0)` — it does not cross.

## Worked example 3 — completing the square
Rewrite `x² + 6x + 2` in vertex form:

1. `x² + 6x = (x + 3)² − 9`
2. So `x² + 6x + 2 = (x + 3)² − 7`
3. Vertex form: `y = (x + 3)² − 7`, vertex at `(−3, −7)`

## Worked example 4 — projectile
A ball is thrown upward with `h(t) = −5t² + 20t`:

- Vertex at `t = 2s`, `h = 20 m` — the **peak height**.
- The ball lands at `h = 0`: `−5t² + 20t = 0  ⇒  t = 0` or `t = 4s`.
- Total flight time: 4 seconds.

## Real-world applications
- **Physics:** parabolic trajectories of projectiles in a vacuum.
- **Optics:** parabolic mirrors focus parallel rays to a single point
  (used in headlights, telescopes, and solar cookers).
- **Finance:** revenue = price · quantity, where quantity often falls
  linearly with price, giving a quadratic revenue curve.
- **Architecture:** the Gateway Arch in St. Louis is a *weighted*
  catenary, but the simple suspension curve is closely approximated by
  a parabola.

## Key ideas to remember
- The discriminant alone tells you **how many** real roots there are.
- Vertex form is best for sketching; factored form is best for roots.
- `c` is the value of the function at `x = 0` — always worth computing.
- If `a < 0`, the vertex is a **maximum**, not a minimum.

## Common pitfalls
- Forgetting the sign of `b` when finding the vertex.
- A double root touches the x-axis but does **not** cross it.
- Quadratic equations with `Δ < 0` are not "unsolvable" — they have
  complex solutions, which are essential in electrical engineering and
  quantum mechanics.
- Forgetting the `−b` in the quadratic formula — a classic source of
  sign errors.
"""),

    # ─── Chapter 3 — Sine Waves ───────────────────────────────────────
    ("trig", "Sine Waves", r"""
# Sine Waves

## Origin and a little history
Hipparchus (2nd century BCE) compiled the first known table of sines
in his astronomical work. The Indian mathematician Aryabhata (5th
century CE) called the function *jya*, which the Arabs transliterated
as *jiba* — and a careless translation turned it into the Latin *sinus*
("bay" or "fold"). The modern symbol `sin(x)` came from the 17th
century.

## Definition
A **sine wave** is any function of the form `y = A·sin(B·x + C) + D`.
Four parameters control its shape entirely: `A` is the **amplitude**,
`B` is the **angular frequency**, `C` is the **phase shift**, and `D`
is the **midline**. Sine waves are the building blocks of sound,
light, alternating current, ocean tides, and any other periodic
phenomenon.

Every periodic signal — no matter how jagged — can be decomposed into
a sum of sine waves by the Fourier transform. That single fact is the
reason sine waves appear in every branch of science.

## Key formulas
- **Amplitude:** `|A|`
- **Period:** `T = 2π / |B|`
- **Angular frequency:** `B` (radians per unit `x`)
- **Frequency:** `f = 1 / T`
- **Phase shift:** `−C / B` (horizontal translation)
- **Vertical shift:** `D` (the midline)
- **Maximum / minimum:** `y_max = D + |A|`,  `y_min = D − |A|`
- **Identities:** `cos(x) = sin(x + π/2)`,  `sin²(x) + cos²(x) = 1`
- **Double angle:** `sin(2x) = 2·sin(x)·cos(x)`
- **Sum:** `sin(a ± b) = sin(a)·cos(b) ± cos(a)·sin(b)`

## Worked example 1 — read the parameters
`y = 3·sin(2·x) + 1`:

| quantity | value |
|---|---|
| `A, B, C, D` | 3, 2, 0, 1 |
| amplitude | 3 |
| period | π ≈ 3.14 |
| midline | y = 1 |
| range | [−2, 4] |

The curve oscillates three units above and three units below the
midline `y = 1`, completing one full cycle every `π` units of `x`.

## Worked example 2 — phase shift
`y = sin(x − π/2)`:

- `C = −π/2`, so phase shift = `−C / B = π/2`
- The wave is shifted **right** by `π/2`.
- It looks exactly like a cosine wave — confirming `cos(x) = sin(x + π/2)`.

## Worked example 3 — adding two waves
Let `y₁ = sin(x)` and `y₂ = 0.5·sin(2x)`. Their sum is the **Fourier**
sum of a sawtooth-like shape. The first term is the fundamental, the
second the first harmonic. The more harmonics we add, the closer the
sum gets to a true sawtooth.

## Real-world applications
- **Music:** every musical note is a sum of sine waves at integer
  multiples of a fundamental frequency.
- **AC power:** the wall outlet delivers a 50/60 Hz sine wave of
  voltage.
- **Waves:** sound, light, ocean swells, and electromagnetic
  radiation are all sinusoidal in their simplest form.
- **Pendulums:** for small angles, the position of a pendulum is
  approximately sinusoidal.

## Key ideas to remember
- A larger `|B|` means a **shorter** period — the wave compresses.
- A larger `|A|` means a **taller** wave — the wave stretches.
- The phase shift moves the wave **horizontally**, never vertically.
- Two waves with the same period and phase interfere cleanly — a
  foundation of physics called **superposition**.

## Common pitfalls
- Confusing the period with the frequency: `T = 1/f`.
- Forgetting that cosine is just a phase-shifted sine: they are the
  same wave, drawn from a different starting point.
- Reading `B = 2` as "twice the period" instead of "half the period".
"""),

    # ─── Chapter 4 — Derivatives ─────────────────────────────────────
    ("derivative", "Derivatives", r"""
# Derivatives

## Origin and a little history
The derivative was invented twice — once by Newton (1665) and once by
Leibniz (1675) — to answer the same question: how do you measure the
instantaneous rate of change? Their two notations (`f′(x)` and
`dy/dx`) survive side by side. Newton needed it for gravity and
planetary motion; Leibniz needed it for geometry. The two approaches
were unified a century later by Cauchy, who gave the rigorous
limit-based definition we use today.

## Definition
The **derivative** `f′(x)` of a function `f` at a point `x` is the
instantaneous rate of change — the slope of the tangent line at that
point. Formally, it is the limit of the difference quotient as the
step size `h` shrinks to zero.

The derivative turns geometry into algebra. Instead of drawing
tangents, you compute them. This single idea powers optimisation in
economics, motion in physics, gradients in machine learning, and
sensitivity analysis in engineering.

## Key formulas
- **Limit definition:** `f′(x) = lim[h→0] (f(x+h) − f(x)) / h`
- **Power rule:** `d/dx[xⁿ] = n·xⁿ⁻¹`
- **Sum rule:** `(f + g)′ = f′ + g′`
- **Constant rule:** `d/dx[c] = 0`
- **Product rule:** `(f·g)′ = f′·g + f·g′`
- **Quotient rule:** `(f/g)′ = (f′·g − f·g′) / g²`
- **Chain rule:** `d/dx[f(g(x))] = f′(g(x))·g′(x)`
- **Trig:** `d/dx[sin x] = cos x`,  `d/dx[cos x] = −sin x`
- **Exponential:** `d/dx[eˣ] = eˣ`
- **Logarithm:** `d/dx[ln x] = 1 / x`
- **Inverse functions:** `d/dx[f⁻¹(x)] = 1 / f′(f⁻¹(x))`

## Worked example 1 — power rule
For `f(x) = x²` at `x₀ = 3`:

- `f′(x) = 2x`  (power rule)
- `f′(3) = 6`   (the slope of the tangent at `x = 3`)
- Point: `(3, 9)`
- Tangent line: `y = 6·(x − 3) + 9 = 6x − 9`

The secant line between `x = 2.9` and `x = 3.1` has slope
`(9.61 − 8.41) / 0.2 = 6.0`, matching the derivative exactly as `h → 0`.

## Worked example 2 — product rule
Differentiate `f(x) = x² · sin(x)`:

- `f = x²`,  `g = sin(x)`
- `f′ = 2x`,  `g′ = cos(x)`
- `(f·g)′ = f′·g + f·g′ = 2x·sin(x) + x²·cos(x)`

## Worked example 3 — chain rule
Differentiate `f(x) = sin(x²)`:

- Outer: `sin(u)`, inner: `u = x²`
- `d/du[sin u] = cos u = cos(x²)`
- `du/dx = 2x`
- `d/dx[sin(x²)] = cos(x²) · 2x = 2x·cos(x²)`

## Worked example 4 — optimisation
Find the maximum of `f(x) = −x² + 4x`:

1. `f′(x) = −2x + 4`
2. Set `f′(x) = 0`: `−2x + 4 = 0`  →  `x = 2`
3. `f(2) = −4 + 8 = 4` — the **maximum** value.
4. `f″(x) = −2 < 0` — confirms a maximum (concave down).

## Real-world applications
- **Physics:** velocity is the derivative of position; acceleration is
  the derivative of velocity.
- **Economics:** marginal cost is the derivative of total cost; it
  tells you the cost of producing one more unit.
- **Machine learning:** gradient descent moves weights in the
  direction of `−∇f` (the negative gradient).
- **Biology:** the rate of population growth is the derivative of the
  population function.

## Key ideas to remember
- The derivative is a **function**, not a number — it gives a slope
  at every `x`.
- `f′(x) = 0` marks potential maxima, minima, or saddle points.
- `f″(x) > 0` is concave up (a minimum); `f″(x) < 0` is concave
  down (a maximum).
- The chain rule is the master rule — almost every other rule is a
  special case of it.

## Common pitfalls
- `d/dx[1/x] = −1/x²`, not `+1/x²` — the sign matters.
- Treating the secant slope as the tangent slope — they are equal
  only in the limit.
- Forgetting the chain rule when differentiating compositions like
  `sin(x²)`.
- Confusing `f′(x) = 0` (critical point) with `f″(x) = 0` (possible
  inflection).
"""),

    # ─── Chapter 5 — Integrals ───────────────────────────────────────
    ("integral", "Integrals", r"""
# Integrals

## Origin and a little history
Archimedes (3rd century BCE) computed the area of a circle and a
parabola by a method that was, in essence, integration. He split shapes
into infinitely many thin strips and added them up. Two thousand years
later, Newton and Leibniz independently realised that integration and
differentiation are inverses — the *fundamental theorem of calculus*.
That insight unified geometry, physics, and analysis into the modern
form of calculus.

## Definition
The **definite integral** `∫[a, b] f(x) dx` is the signed area between
the curve `f(x)` and the x-axis, from `x = a` to `x = b`. The
**indefinite integral** `∫f(x) dx` is a family of antiderivatives.

Riemann sums approximate the integral with rectangles; finer partitions
mean better accuracy. The **fundamental theorem of calculus** ties
integrals to derivatives: the integral of a derivative is the
original function. Differentiation and integration are inverse
operations.

## Key formulas
- **Left Riemann sum:** `Σᵢ f(xᵢ)·Δx`
- **Right Riemann sum:** `Σᵢ f(xᵢ₊₁)·Δx`
- **Midpoint rule:** `Σᵢ f((xᵢ + xᵢ₊₁)/2)·Δx`
- **Trapezoid rule:** `Σᵢ (f(xᵢ) + f(xᵢ₊₁))/2 · Δx`
- **Simpson's rule:** `(Δx/3)·[f(x₀) + 4·f(x₁) + 2·f(x₂) + 4·f(x₃) + … + f(xₙ)]`
- **Fundamental theorem:** `∫[a, b] f = F(b) − F(a)`
- **Power rule:** `∫xⁿ dx = xⁿ⁺¹ / (n+1) + C`
- **Exponential:** `∫eˣ dx = eˣ + C`
- **Trig:** `∫sin(x) dx = −cos(x) + C`,  `∫cos(x) dx = sin(x) + C`
- **Logarithm:** `∫(1/x) dx = ln|x| + C`
- **Constant multiple:** `∫c·f(x) dx = c·∫f(x) dx`
- **Sum:** `∫(f + g) dx = ∫f dx + ∫g dx`
- **Substitution:** `∫f(g(x))·g′(x) dx = ∫f(u) du`  with `u = g(x)`
- **By parts:** `∫u·dv = u·v − ∫v·du`

## Worked example 1 — midpoint estimate
Estimate `∫[0, 4] x²/4 dx` with the midpoint rule, `n = 4`:

- `Δx = 1`
- Sample points: 0.5, 1.5, 2.5, 3.5
- Heights: `0.5²/4 = 0.0625`, `1.5²/4 = 0.5625`, `2.5²/4 = 1.5625`, `3.5²/4 = 3.0625`
- Sum: `0.0625 + 0.5625 + 1.5625 + 3.0625 = 5.25`
- Exact value: `F(4) − F(0) = (4³/12) − 0 = 64/12 ≈ 5.333`

The midpoint estimate is within 2 % of the true value.

## Worked example 2 — power rule
`∫(3x² + 2x − 1) dx`:

- `∫3x² dx = x³`
- `∫2x dx = x²`
- `∫−1 dx = −x`
- Answer: `x³ + x² − x + C`

## Worked example 3 — definite integral
`∫[1, 3] (2x + 4) dx`:

- Antiderivative: `F(x) = x² + 4x`
- `F(3) − F(1) = (9 + 12) − (1 + 4) = 21 − 5 = 16`

Geometrically: this is the area of a trapezoid with parallel sides
`2·1+4 = 6` and `2·3+4 = 10`, width `3 − 1 = 2`. Area:
`½·(6 + 10)·2 = 16`. ✓

## Worked example 4 — integration by parts
`∫x·eˣ dx`:

- `u = x`, `dv = eˣ dx`
- `du = dx`, `v = eˣ`
- `∫u·dv = u·v − ∫v·du = x·eˣ − ∫eˣ dx = x·eˣ − eˣ + C = eˣ·(x − 1) + C`

## Real-world applications
- **Physics:** work is the integral of force over distance; energy is
  the integral of power over time.
- **Probability:** probabilities are integrals of density functions.
- **Economics:** consumer surplus is the area between a demand curve
  and the price line.
- **Biology:** total biomass is the integral of density over volume.

## Key ideas to remember
- `∫f dx` returns a **family** of functions; `∫[a,b] f dx` returns a
  **number**.
- Always add `+ C` to indefinite integrals; the constant is the
  information lost in differentiation.
- For monotonic functions, left and right Riemann sums bracket the
  true integral.
- The fundamental theorem turns integration into subtraction — the
  hardest problem in calculus is reduced to finding an antiderivative.

## Common pitfalls
- Forgetting the absolute value: `∫(1/x) dx = ln|x| + C`, not `ln x + C`.
- Mixing up "antiderivative" with "integral" — they are connected but
  not the same idea.
- Treating Riemann sums as exact — they are approximations, and
  converge to the integral only in the limit.
- Dropping the `+ C` on indefinite integrals.
"""),

    # ─── Chapter 6 — Geometry ────────────────────────────────────────
    ("geometry", "Geometry", r"""
# Geometry

## Origin and a little history
Geometry began in the Nile valley — Egyptian surveyors ("rope
stretchers") re-measured farmland after the annual floods around
3000 BCE. The Greeks turned measurement into proof: Thales, Pythagoras,
Euclid, and Apollonius built the logical edifice we still use. Euclid's
*Elements* (300 BCE) was the standard mathematics textbook for over
two thousand years — used in schools into the 20th century.

## Definition
Geometry is the study of **shapes** and their **measurements**. Every
shape has formulas for its perimeter, area, surface area, and
volume. The same handful of ideas — angles, similarity, congruence,
the Pythagorean theorem — appears across all of them.

In this chapter we collect the formulas for the shapes you will meet
most often: triangles, circles, quadrilaterals, and regular polygons.

## Key formulas
- **Circle:** `C = 2πr`,  `A = π·r²`
- **Triangle (any):** `A = ½·b·h`
- **Triangle (Heron):** `A = √(s(s−a)(s−b)(s−c))`,  `s = (a+b+c)/2`
- **Right triangle:** `c = √(a² + b²)`,  `A = ½ab`
- **Equilateral triangle:** `A = (√3/4)·s²`
- **Rectangle:** `A = l·w`,  `P = 2(l + w)`
- **Rhombus:** `A = ½·p·q`  (p, q = diagonals)
- **Trapezoid:** `A = ½·(b₁ + b₂)·h`
- **Regular n-gon:** `A = ½·n·s·a`  (a = apothem, s = side)
- **Interior angle sum:** `(n − 2)·180°`
- **Sphere:** `V = (4/3)·π·r³`,  `S = 4π·r²`
- **Cylinder:** `V = π·r²·h`,  `S = 2π·r·(r + h)`
- **Cone:** `V = (1/3)·π·r²·h`,  `S = π·r·(r + s)`  (s = slant)
- **Pyramid:** `V = (1/3)·B·h`  (B = base area)

## Worked example 1 — right triangle
A right triangle with legs 3 and 4:

| quantity | value |
|---|---|
| hypotenuse | √(9 + 16) = 5 |
| area | ½ · 3 · 4 = 6 |
| perimeter | 3 + 4 + 5 = 12 |
| angle opposite 3 | arctan(3/4) ≈ 36.87° |
| angle opposite 4 | arctan(4/3) ≈ 53.13° |

This is the famous **3-4-5** right triangle — the smallest integer
right triangle. It has been used by surveyors for thousands of years.

## Worked example 2 — Heron's formula
Triangle with sides 7, 8, 9:

- `s = (7+8+9)/2 = 12`
- `A = √(12·5·4·3) = √720 = 12·√5 ≈ 26.83`

## Worked example 3 — circle and sector
A circle of radius 6 with a central angle of 60°:

- Full circumference: `2π·6 = 12π ≈ 37.70`
- Arc length: `(60/360) · 12π = 2π ≈ 6.28`
- Full area: `π·36 ≈ 113.10`
- Sector area: `(60/360) · 113.10 ≈ 18.85`

## Worked example 4 — sphere and cylinder
A sphere of radius 5 fits exactly inside a cylinder of radius 5 and
height 10:

- Sphere volume: `(4/3)·π·125 = 500π/3 ≈ 523.6`
- Cylinder volume: `π·25·10 = 250π ≈ 785.4`
- Ratio: **2 / 3** — Archimedes' famous result.

## Real-world applications
- **Architecture:** load-bearing arches are circular or parabolic;
  columns are cylindrical.
- **Navigation:** great-circle routes on a sphere are arcs of great
  circles (geodesics).
- **Engineering:** the strength of a beam depends on the second
  moment of area of its cross-section — a geometric property.
- **Art:** the golden ratio `φ ≈ 1.618` appears in the dimensions of
  rectangles considered most pleasing to the eye.

## Key ideas to remember
- The Pythagorean theorem works **only** for right triangles.
- Two triangles are similar (same shape) iff their angles match; two
  are congruent (same shape and size) iff all three sides match.
- The area of any shape is invariant under rigid motions — rotating or
  translating a figure does not change its area.
- Archimedes' two classical results: the sphere is 2/3 of its
  circumscribing cylinder; the cylinder is 3/2 of its inscribed
  sphere.

## Common pitfalls
- Confusing "radius" with "diameter" — diameter is twice the radius.
- Heron's formula needs the three side lengths, not the coordinates.
- Forgetting that a degenerate triangle (collinear points) has area
  zero and is not a true triangle.
- Treating "perimeter" and "area" as interchangeable — they answer
  completely different questions.
"""),

    # ─── Chapter 7 — Linear Transforms ────────────────────────────────
    ("transform", "Linear Transforms", r"""
# Linear Transforms

## Origin and a little history
The mathematics of linear transformations matured in three stages.
First, Hamilton and Grassmann (mid-19th century) formalised vectors
and their operations. Then Cayley and Sylvester invented matrix
algebra in the 1850s. Finally, group theory (Lie, Klein) revealed
that the **set of all linear transformations is a group** — meaning
the composition, identity, and inverse behave like a closed system.
Computer graphics, robotics, and quantum mechanics all live inside
this group.

## Definition
A 2×2 matrix `M = [[a, b], [c, d]]` defines a **linear transformation**
that maps the plane to itself by sending the point `(x, y)` to
`(a·x + b·y, c·x + d·y)`. The columns of `M` are the images of the
standard basis vectors `î = (1, 0)` and `ĵ = (0, 1)` — knowing where
the basis goes determines the entire transformation.

Every linear transformation stretches, squeezes, shears, rotates, or
reflects the plane. It never bends it. The determinant of `M` tells
you how areas scale; the sign of the determinant tells you whether
orientation is preserved or reversed.

## Key formulas
- **Apply to a point:** `M·(x, y) = (a·x + b·y, c·x + d·y)`
- **Determinant:** `det(M) = a·d − b·c`
- **Inverse (when det ≠ 0):** `M⁻¹ = (1/det)·[[d, −b], [−c, a]]`
- **Trace:** `tr(M) = a + d`
- **Rotation by θ:** `R(θ) = [[cos θ, −sin θ], [sin θ, cos θ]]`
- **Uniform scale by k:** `S(k) = [[k, 0], [0, k]]`
- **Horizontal shear:** `H(k) = [[1, k], [0, 1]]`
- **Reflection across x-axis:** `[[1, 0], [0, −1]]`
- **Reflection across y-axis:** `[[−1, 0], [0, 1]]`
- **Composition:** `(M·N)·v = M·(N·v)`  (note: order matters)
- **Area scaling:** `area(M·region) = |det M| · area(region)`
- **Eigenvalues:** solve `det(M − λ·I) = 0`
- **Eigenvectors:** solve `(M − λ·I)·v = 0`

## Worked example 1 — rotation by 90°
The matrix `M = [[0, −1], [1, 0]]` rotates the plane by 90°:

- `(1, 0) → (0, 1)`     (the basis vector î points up)
- `(0, 1) → (−1, 0)`    (ĵ points left)
- `det M = 0·0 − (−1)·1 = 1`
- Area is preserved (`|det| = 1`) and orientation is preserved
  (positive determinant).

## Worked example 2 — singular transform
`M = [[1, 2], [2, 4]]`:

- `det M = 1·4 − 2·2 = 0` — **singular**.
- Every point on the plane is collapsed to the line `y = 2x`.
- No inverse exists — you cannot undo a singular transformation.

## Worked example 3 — eigenvalues
For `M = [[3, 1], [0, 2]]`:

1. Characteristic equation: `det(M − λ·I) = (3−λ)(2−λ) − 0 = 0`
2. Eigenvalues: `λ₁ = 3`,  `λ₂ = 2`
3. For `λ₁ = 3`: `(M − 3·I)·v = 0  ⇒  [[0, 1], [0, −1]]·v = 0`
   → eigenvector `(1, 0)` — the x-axis is unchanged.
4. For `λ₂ = 2`: eigenvector `(1, −1)`.

The two eigenvectors are the directions the matrix only **stretches**
(without rotating).

## Worked example 4 — composition
Rotate by 90° then scale by 2:

- `S(2)·R(90°) = [[2, 0], [0, 2]]·[[0, −1], [1, 0]] = [[0, −2], [2, 0]]`
- Test: `(1, 0) → (0, 1) → (0, 2)` — first rotated, then scaled. ✓

Reverse the order — `R(90°)·S(2)` — and the result differs.

## Real-world applications
- **Computer graphics:** every 3D rendering is built from rotations,
  translations, and projections — all linear (or affine)
  transformations.
- **Robotics:** a robot arm's joint positions are combined with
  rotation matrices to compute the location of its end-effector.
- **Quantum mechanics:** the state of a quantum system is a vector in
  a Hilbert space, and physical operations are linear
  transformations.
- **Image processing:** filters, scaling, blurring, and edge detection
  are all linear operations on pixel arrays.

## Key ideas to remember
- The determinant is a **volume** (or area) — its absolute value tells
  you how much regions are scaled.
- Composition `M·N` is **not** commutative — order matters.
- Eigenvectors of `M` are the directions that `M` leaves unchanged
  (up to scale). They are the "axes" of the transformation.
- Singular matrices (`det = 0`) collapse information — they have no
  inverse and cannot be undone.

## Common pitfalls
- `det M = 0` means `M` is **singular** — it collapses the plane onto a
  line, and no inverse exists.
- "Flip" transforms (reflections) have negative determinants; pure
  rotations and uniform scales have positive ones.
- Treating matrix multiplication as commutative — it almost never is.
- Forgetting the `+1` when going from linear to affine transformations
  (those add a translation).
"""),
]


class Command(BaseCommand):
    help = "Create 7 in-depth reading-room chapters (idempotent)."

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
