"""5+ unit tests per mathlib module — no Django views."""

import math

from django.test import SimpleTestCase

from apps.explorer.mathlib import linear, quadratic, trig, derivative, integral, geometry, transform
from apps.explorer.mathlib.geometry import SHAPE_DEFAULTS, SHAPES


class LinearTests(SimpleTestCase):
    def test_compute_basic(self):
        c = linear.compute(2.0, 1.0)
        self.assertAlmostEqual(c["fn"](0), 1.0)
        self.assertAlmostEqual(c["fn"](3), 7.0)
        self.assertAlmostEqual(c["slope"], 2.0)
        self.assertAlmostEqual(c["y_intercept"], 1.0)
        self.assertAlmostEqual(c["x_intercept"], -0.5)
        self.assertAlmostEqual(c["angle_deg"], math.degrees(math.atan(2)))

    def test_zero_slope_horizontal(self):
        c = linear.compute(0, 5)
        self.assertTrue(math.isnan(c["x_intercept"]))
        self.assertEqual(c["angle_deg"], 0.0)

    def test_negative_slope(self):
        c = linear.compute(-3, 6)
        self.assertAlmostEqual(c["x_intercept"], 2.0)
        self.assertLess(c["angle_deg"], 0)

    def test_steps_structure(self):
        s = linear.steps(1, 0, 0, 0)
        self.assertGreaterEqual(len(s), 5)
        for step in s:
            self.assertIn("text", step)

    def test_solvers_complete(self):
        sv = linear.solvers()
        for sym in ("m", "b", "x", "y"):
            self.assertIn(sym, sv["solvers"])
            self.assertIn("formula", sv["solvers"][sym])
            self.assertIn("compute_js", sv["solvers"][sym])


class QuadraticTests(SimpleTestCase):
    def test_vertex(self):
        c = quadratic.compute(1, -4, 3)  # x²−4x+3, vertex (2, −1)
        self.assertAlmostEqual(c["vertex_x"], 2.0)
        self.assertAlmostEqual(c["vertex_y"], -1.0)

    def test_two_roots(self):
        c = quadratic.compute(1, -5, 6)  # roots 2, 3
        self.assertEqual(c["nature"], "Two real roots")
        self.assertEqual(c["roots"], [2.0, 3.0])

    def test_one_repeated(self):
        c = quadratic.compute(1, -2, 1)  # (x-1)²
        self.assertEqual(c["nature"], "One repeated root")
        self.assertEqual(c["roots"], [1.0, 1.0])

    def test_no_real(self):
        c = quadratic.compute(1, 0, 1)
        self.assertEqual(c["nature"], "No real roots")
        self.assertEqual(c["roots"], [])

    def test_opens(self):
        self.assertIn("upward", quadratic.compute(1, 0, 0)["opens"])
        self.assertIn("downward", quadratic.compute(-1, 0, 0)["opens"])


class TrigTests(SimpleTestCase):
    def test_amplitude(self):
        c = trig.compute(3, 1, 0, 0)
        self.assertAlmostEqual(c["amplitude"], 3.0)

    def test_period(self):
        c = trig.compute(1, 2, 0, 0)
        self.assertAlmostEqual(c["period"], math.pi)

    def test_phase_shift(self):
        c = trig.compute(1, 1, 1, 0)
        self.assertAlmostEqual(c["phase_shift"], -1.0)

    def test_midline(self):
        c = trig.compute(1, 1, 0, 5)
        self.assertAlmostEqual(c["midline"], 5.0)

    def test_solvers(self):
        sv = trig.solvers()
        self.assertIn("y", sv["solvers"])


class DerivativeTests(SimpleTestCase):
    def test_poly_slope(self):
        c = derivative.compute("poly", 3.0, 0.5)
        self.assertAlmostEqual(c["y0"], 9.0)
        self.assertAlmostEqual(c["slope_exact"], 6.0, places=3)

    def test_sin_slope(self):
        c = derivative.compute("sin", 0.0, 0.5)
        self.assertAlmostEqual(c["y0"], 0.0, places=6)
        self.assertAlmostEqual(c["slope_exact"], 1.0, places=4)

    def test_cubic_slope(self):
        c = derivative.compute("cubic", 1.0, 0.1)
        self.assertAlmostEqual(c["slope_exact"], 0.0, places=3)  # 3·1²-3 = 0

    def test_exp_slope(self):
        c = derivative.compute("exp", 0.0, 0.1)
        # f'(0) = (1/3)·e^0 = 1/3
        self.assertAlmostEqual(c["slope_exact"], 1/3, places=3)

    def test_solvers(self):
        sv = derivative.solvers()
        self.assertIn("y", sv["solvers"])


class IntegralTests(SimpleTestCase):
    def test_riemann_approaches_exact(self):
        c = integral.compute("poly", 0, 4, 1000, "midpoint")
        # ∫₀⁴ x²/4 dx = (64/12) = 5.333...
        self.assertAlmostEqual(c["riemann"], 64/12, places=2)
        self.assertAlmostEqual(c["exact"],   64/12, places=2)

    def test_left_right_differ(self):
        cl = integral.compute("poly", 0, 4, 10, "left")
        cr = integral.compute("poly", 0, 4, 10, "right")
        self.assertNotAlmostEqual(cl["riemann"], cr["riemann"])

    def test_bars_shape(self):
        c = integral.compute("poly", 0, 4, 8, "trapezoid")
        self.assertEqual(len(c["bars"]), 8)
        for bar in c["bars"]:
            self.assertIn("x1", bar)

    def test_zero_width(self):
        c = integral.compute("poly", 3, 3, 5, "midpoint")
        self.assertEqual(c["riemann"], 0.0)
        self.assertEqual(c["dx"], 0.0)

    def test_methods_meta(self):
        from apps.explorer.mathlib.integral import methods_meta
        self.assertGreater(len(methods_meta()), 0)


class GeometryTests(SimpleTestCase):
    def test_circle(self):
        c = geometry.compute("circle", r=2, cx=0, cy=0)
        self.assertAlmostEqual(c["diameter"], 4)
        self.assertAlmostEqual(c["area"], math.pi * 4, places=4)

    def test_square(self):
        c = geometry.compute("square", s=3)
        self.assertEqual(c["perimeter"], 12)
        self.assertAlmostEqual(c["diagonal"], 3 * math.sqrt(2))

    def test_right_triangle(self):
        c = geometry.compute("rightTriangle", a=3, b=4)
        self.assertAlmostEqual(c["c"], 5)
        self.assertAlmostEqual(c["area"], 6)
        self.assertAlmostEqual(c["gamma"], 90.0)

    def test_rhombus_area(self):
        c = geometry.compute("rhombus", p=6, q=4)
        self.assertAlmostEqual(c["area"], 12)

    def test_polygon_vertices(self):
        c = geometry.compute("polygon", n=6, r=2, rotation_deg=0)
        self.assertEqual(len(c["vertices"]), 6)
        self.assertAlmostEqual(c["perimeter"], 12 * math.sin(math.pi/6) * 2)  # 2rsin(π/n)·n
        self.assertAlmostEqual(c["interior"], 120)

    def test_all_shapes_have_defaults(self):
        for s in SHAPES:
            self.assertIn(s, SHAPE_DEFAULTS)


class TransformTests(SimpleTestCase):
    def test_identity(self):
        c = transform.compute(1, 0, 0, 1)
        self.assertEqual(c["transformed"], c["original"])
        self.assertEqual(c["det"], 1.0)

    def test_rotate_90(self):
        c = transform.compute(0, -1, 1, 0)
        self.assertEqual(c["i_hat"], (0, 1))
        self.assertEqual(c["j_hat"], (-1, 0))
        self.assertEqual(c["det"], 1.0)
        self.assertEqual(c["orientation"], "preserved")

    def test_singular(self):
        c = transform.compute(1, 2, 2, 4)  # rows linearly dependent
        self.assertTrue(c["singular"])
        self.assertEqual(c["det"], 0.0)

    def test_flip(self):
        c = transform.compute(-1, 0, 0, 1)
        self.assertLess(c["det"], 0)
        self.assertEqual(c["orientation"], "flipped")

    def test_presets(self):
        self.assertEqual(len(transform.PRESETS), 6)
        for p in transform.PRESETS:
            self.assertIn("a", p)
            self.assertIn("b", p)
            self.assertIn("c", p)
            self.assertIn("d", p)
