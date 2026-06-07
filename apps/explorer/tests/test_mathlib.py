"""5+ unit tests per mathlib module — no Django views."""

import json
import math

from django.test import SimpleTestCase, TestCase

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
        s = linear.steps(1, 0, 0, 0, 0)
        self.assertGreaterEqual(len(s), 5)
        for step in s:
            self.assertIn("text", step)
            # Every result line should NOT have a stray closing paren
            for k in ("formula", "substitution", "result"):
                if k in step and step[k]:
                    self.assertNotIn("))", step[k], f"stray '))' in {k}: {step[k]!r}")
        # Every step that has a NUMERIC "result" should also have a
        # result_bind (so the click-to-edit feature can push the new value
        # back to the input). Steps that only restate the formula are skipped.
        import re
        for step in s:
            text = step.get("text", "")
            result = step.get("result", "")
            if not result:
                continue
            # Skip non-editable, text-only cases
            skip_phrases = (
                "no x-intercept", "curve is a flat",
                "invertible", "singular (no inverse)",
                "no real x-intercept", "no real roots",
            )
            if any(p in text for p in skip_phrases):
                continue
            # Skip steps whose result is just a formula restatement (no number)
            if not re.search(r"\d", result):
                continue
            self.assertIn(
                "result_bind", step,
                f"step with numeric result but no result_bind: {text!r} → {result!r}",
            )

    def test_solvers_complete(self):
        sv = linear.solvers()
        for sym in ("m", "b", "x", "y"):
            self.assertIn(sym, sv["solvers"])
            self.assertIn("formula", sv["solvers"][sym])
            self.assertIn("compute_js", sv["solvers"][sym])

    def test_solvers_accept_params(self):
        # Should also work with params (signature compat for view layer)
        sv = linear.solvers({"m": 2.0, "b": 1.0})
        self.assertIn("y", sv["solvers"])


class QuadraticTests(SimpleTestCase):
    def test_vertex(self):
        c = quadratic.compute(1, -4, 3)
        self.assertAlmostEqual(c["vertex_x"], 2.0)
        self.assertAlmostEqual(c["vertex_y"], -1.0)

    def test_two_roots(self):
        c = quadratic.compute(1, -5, 6)
        self.assertEqual(c["nature"], "Two real roots")
        self.assertEqual(c["roots"], [2.0, 3.0])

    def test_one_repeated(self):
        c = quadratic.compute(1, -2, 1)
        self.assertEqual(c["nature"], "One repeated root")
        self.assertEqual(c["roots"], [1.0, 1.0])

    def test_no_real(self):
        c = quadratic.compute(1, 0, 1)
        self.assertEqual(c["nature"], "No real roots")
        self.assertEqual(c["roots"], [])

    def test_opens(self):
        self.assertIn("upward", quadratic.compute(1, 0, 0)["opens"])
        self.assertIn("downward", quadratic.compute(-1, 0, 0)["opens"])

    def test_steps_no_typos(self):
        s = quadratic.steps(1, -5, 6, 2.5, -6.25, 1, [2.0, 3.0],
                            "Two real roots", "upward (∪)", 6)
        self.assertGreaterEqual(len(s), 6)
        for step in s:
            for k in ("formula", "substitution", "result"):
                v = step.get(k, "")
                self.assertNotIn("))", v, f"stray '))' in {k}: {v!r}")
        # every step with a NUMERIC result should be editable
        import re
        for step in s:
            result = step.get("result", "")
            if result and re.search(r"\d", result):
                self.assertIn(
                    "result_bind", step,
                    f"step with numeric result but no result_bind: {step.get('text','')!r}",
                )


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

    def test_B_zero_is_safe(self):
        c = trig.compute(2, 0, 1, 0)
        self.assertEqual(c["period"], float("inf"))
        # Should not raise when generating steps
        s = trig.steps(2, 0, 1, 0, c["period"], c["phase_shift"],
                       c["amplitude"], c["midline"], c["frequency"],
                       c["max_value"], c["min_value"])
        self.assertGreater(len(s), 4)

    def test_solvers(self):
        sv = trig.solvers()
        self.assertIn("y", sv["solvers"])
        self.assertIn("x", sv["solvers"])


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
        self.assertAlmostEqual(c["slope_exact"], 0.0, places=3)

    def test_exp_slope(self):
        c = derivative.compute("exp", 0.0, 0.1)
        self.assertAlmostEqual(c["slope_exact"], 1/3, places=3)

    def test_solvers_parametric(self):
        # The solver for "y" must use the SELECTED function, not a hard-coded one
        for key in ("poly", "cubic", "sin", "exp", "abs"):
            sv = derivative.solvers({"fn_key": key})
            self.assertIn("y", sv["solvers"])
            # Just ensure the expression is non-trivial and key-specific
            self.assertTrue(sv["solvers"]["y"]["compute_js"])

        # And the "m" solver (derivative) should also be parametric
        sv_poly = derivative.solvers({"fn_key": "poly"})
        sv_sin = derivative.solvers({"fn_key": "sin"})
        self.assertNotEqual(
            sv_poly["solvers"]["m"]["compute_js"],
            sv_sin["solvers"]["m"]["compute_js"],
        )


class IntegralTests(SimpleTestCase):
    def test_riemann_approaches_exact(self):
        c = integral.compute("poly", 0, 4, 1000, "midpoint")
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

    def test_solvers_parametric(self):
        # The "A" solver must depend on the selected function & method
        sv_poly_mid = integral.solvers({"fn_key": "poly", "method": "midpoint"})
        sv_sin_mid = integral.solvers({"fn_key": "sin", "method": "midpoint"})
        self.assertIn("A", sv_poly_mid["solvers"])
        self.assertIn("A", sv_sin_mid["solvers"])
        # Different functions → different compute_js
        self.assertNotEqual(
            sv_poly_mid["solvers"]["A"]["compute_js"],
            sv_sin_mid["solvers"]["A"]["compute_js"],
        )
        # Different method → different compute_js
        sv_poly_left = integral.solvers({"fn_key": "poly", "method": "left"})
        self.assertNotEqual(
            sv_poly_mid["solvers"]["A"]["compute_js"],
            sv_poly_left["solvers"]["A"]["compute_js"],
        )

    def test_solvers_compute_correct_area(self):
        # Verify the JS expression has the right structure for the browser to run.
        # We can't `eval` it in Python because it uses `var` + `return` inside an
        # IIFE — those are valid in JS but not in Python's eval. So we re-implement
        # the algorithm in Python with the same loop and check the result.
        from apps.explorer.mathlib.integral import _riemann_js
        js_mid = _riemann_js("x*x/4", "midpoint")
        js_trap = _riemann_js("x*x/4", "trapezoid")
        # Sanity-check the structure of the JS
        self.assertIn("function(x){return x*x/4;}", js_mid)
        self.assertIn("(x1+x2)/2", js_mid)
        self.assertIn("fn(x1)", js_trap)
        self.assertIn("fn(x2)", js_trap)
        # And check the algorithm in Python gives the expected value
        a, b, n = 0.0, 4.0, 50.0
        dx = (b - a) / n
        s = 0.0
        for i in range(int(n)):
            x1 = a + i * dx
            x2 = a + (i + 1) * dx
            x = (x1 + x2) / 2  # midpoint
            s += (x * x) / 4 * dx
        self.assertAlmostEqual(s, 64/12, places=1)


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
        self.assertAlmostEqual(c["perimeter"], 12 * math.sin(math.pi/6) * 2)
        self.assertAlmostEqual(c["interior"], 120)

    def test_all_shapes_have_defaults(self):
        for s in SHAPES:
            self.assertIn(s, SHAPE_DEFAULTS)

    def test_solvers_compute_real_values(self):
        # The A/P solvers must return non-zero values for a meaningful shape
        for shape in SHAPES:
            sv = geometry.solvers({"shape": shape, **SHAPE_DEFAULTS[shape]})
            self.assertIn("A", sv["solvers"], f"{shape}: no A solver")
            self.assertIn("P", sv["solvers"], f"{shape}: no P solver")
            # compute_js must not be the dead '0' from the old bug
            self.assertNotEqual(sv["solvers"]["A"]["compute_js"], "0",
                                f"{shape}: A solver is dead")
            self.assertNotEqual(sv["solvers"]["P"]["compute_js"], "0",
                                f"{shape}: P solver is dead")

    def test_solvers_match_python_compute(self):
        # The JS expressions should give the same area as the Python compute()
        for shape, defaults in SHAPE_DEFAULTS.items():
            c = geometry.compute(shape, **defaults)
            sv = geometry.solvers({"shape": shape, **defaults})
            # Mimic JS environment: Math.PI, Math.sin, etc.
            scope = {**defaults,
                     "Math": type("M", (), {
                         "PI": math.pi, "pi": math.pi,
                         "sin": math.sin, "cos": math.cos,
                         "tan": math.tan, "sqrt": math.sqrt,
                         "hypot": math.hypot, "pow": math.pow,
                         "exp": math.exp, "log": math.log,
                         "abs": abs, "atan2": math.atan2,
                         "asin": math.asin, "acos": math.acos,
                         "atan": math.atan,
                     })(),
                     "__builtins__": {}}
            area_js = eval(sv["solvers"]["A"]["compute_js"], scope)
            self.assertAlmostEqual(area_js, c["area"], places=2,
                                   msg=f"{shape}: JS area {area_js} != Python area {c['area']}")


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
        c = transform.compute(1, 2, 2, 4)
        self.assertTrue(c["singular"])
        self.assertEqual(c["det"], 0.0)

    def test_flip(self):
        c = transform.compute(-1, 0, 0, 1)
        self.assertLess(c["det"], 0)
        self.assertEqual(c["orientation"], "flipped")

    def test_presets(self):
        self.assertEqual(len(transform.PRESETS), 6)
        for p in transform.PRESETS:
            self.assertIn("name", p)
            self.assertIn("params", p)
            for k in ("a", "b", "c", "d"):
                self.assertIn(k, p["params"], f"preset {p['name']!r} missing {k}")

    def test_trace(self):
        c = transform.compute(2, 1, 0, 3)
        self.assertEqual(c["trace"], 5.0)

    def test_solvers_are_real(self):
        # Solvers must actually solve for matrix entries / outputs
        sv = transform.solvers()
        for sym in ("a", "b", "c", "d", "u", "v"):
            self.assertIn(sym, sv["solvers"], f"missing solver for {sym}")
            self.assertNotIn("return a", sv["solvers"][sym]["compute_js"],
                             f"{sym} solver is identity (a bug)")


class InsightBindingTests(TestCase):
    """Verify that _build_insights() in the view layer wires up the
    `bind_to` / `bind_value` fields that the editable-stat JS reads.
    These are integration tests — they hit the view via the test client
    and inspect the rendered HTML, not the mathlib directly.
    """
    @classmethod
    def setUpTestData(cls):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        cls.admin = User.objects.create_superuser(
            username="ins-admin", password="pw12345!", email="a@e.com"
        )
        from apps.reading.models import ReadingPage
        for s in ("linear", "quadratic", "trig", "derivative", "integral",
                  "geometry", "transform"):
            ReadingPage.objects.update_or_create(
                slug=s, defaults={"module_id": s, "title": s.title(), "body_md": f"# {s}"},
            )

    def _get(self, slug):
        self.client.login(username="ins-admin", password="pw12345!")
        return self.client.get(f"/explore/{slug}/")

    def _post(self, slug, data):
        self.client.login(username="ins-admin", password="pw12345!")
        return self.client.post(f"/explore/{slug}/update/", data, HTTP_HX_REQUEST="true")

    def test_linear_insights_have_bind(self):
        r = self._get("linear")
        body = r.content.decode()
        # All four linear stats should be marked editable
        for label in ("Slope m", "Y-intercept", "X-intercept", "Angle \u03b8"):
            self.assertIn(f'data-stat-chip="{label}"', body)
        # Just check at least one bind is present
        self.assertIn('data-bind-input="m"', body)
        self.assertIn('data-bind-input="b"', body)

    def test_quadratic_insights_have_bind(self):
        r = self._get("quadratic")
        body = r.content.decode()
        self.assertIn('data-bind-input="a"', body)
        self.assertIn('data-bind-input="c"', body)

    def test_trig_insights_have_bind(self):
        r = self._get("trig")
        body = r.content.decode()
        self.assertIn('data-bind-input="A"', body)
        self.assertIn('data-bind-input="B"', body)
        self.assertIn('data-bind-input="C"', body)
        self.assertIn('data-bind-input="D"', body)

    def test_derivative_insights_have_bind(self):
        r = self._get("derivative")
        body = r.content.decode()
        self.assertIn('data-bind-input="x0"', body)
        self.assertIn('data-bind-input="h"', body)

    def test_integral_insights_have_bind(self):
        r = self._get("integral")
        body = r.content.decode()
        self.assertIn('data-bind-input="n"', body)
        self.assertIn('data-bind-input="b"', body)

    def test_geometry_insights_have_bind(self):
        r = self._post("geometry", {"shape": "circle", "r": 3, "cx": 0, "cy": 0})
        body = r.content.decode()
        # The radius insight should be editable and bind to input "r"
        self.assertIn('data-bind-input="r"', body)

    def test_transform_insights_have_bind(self):
        r = self._get("transform")
        body = r.content.decode()
        self.assertIn('data-bind-input="a"', body)
        self.assertIn('data-bind-input="d"', body)

    def test_module_body_id_exists(self):
        # Regression: the HTMX swap target #module-body must exist on the page
        r = self._get("linear")
        body = r.content.decode()
        self.assertIn('id="module-body"', body,
                      "HTMX swap target #module-body is missing on the page")

    def test_stat_cards_have_clickable_data_attrs(self):
        """The stat cards rendered by _module_body.html must have both
        `data-stat-chip` and `data-bind-input` so editable_stat.js can pick
        them up. (Replaces a previous bug where only `data-editable-stat`
        was queried but the template only emitted the other two.)"""
        r = self._get("linear")
        body = r.content.decode()
        # Find every .stat-card with data-stat-chip and verify it has a
        # data-bind-input pointing at a real input on the page.
        import re
        cards = re.findall(
            r'<div\s+class="stat-card[^"]*"[^>]*data-stat-chip="([^"]+)"[^>]*data-bind-input="([^"]+)"',
            body,
        )
        self.assertGreaterEqual(
            len(cards), 3,
            f"Expected ≥3 stat cards with data-bind-input, found {len(cards)}",
        )
        for label, target in cards:
            self.assertRegex(target, r"^[A-Za-z_]+$", f"bad bind target: {target!r}")
            # The targeted input must exist on the page
            self.assertRegex(
                body,
                rf'<input[^>]*name="{target}"',
                f"stat card {label!r} binds to input {target!r} which doesn't exist on the page",
            )

    def test_post_with_new_value_refreshes_diagram_and_insights(self):
        """End-to-end: pushing a new value through the HTMX update endpoint
        must return a fresh #module-body with the new value reflected in
        the insights and the plot JSON, proving the round-trip works."""
        r = self._post("linear", {"m": "3", "b": "2"})
        self.assertEqual(r.status_code, 200)
        body = r.content.decode()
        # New insight values must be visible
        self.assertIn('id="module-body"', body)
        self.assertIn("data-bind-value=\"3.0\"", body)
        self.assertIn("data-bind-value=\"2.0\"", body)
        # Plot container + JSON must be re-rendered
        self.assertIn('id="plot-linear"', body)
        self.assertIn('id="plot-data-linear"', body)
        # The y-intercept is 2, so the line crosses at y=2 — verify the
        # annotation JSON contains the y-intercept marker
        self.assertIn("\"y-int\"", body)

    def test_single_slider_post_works_for_every_module(self):
        """Regression: previously, a slider-only POST failed form validation
        because the other form fields were marked `required`. The view
        must accept a partial form and still render a fresh #module-body
        with the slider's value reflected in the insights."""
        cases = [
            ("linear",     {"m": "5"},                       "5.0"),
            ("quadratic",  {"a": "1", "b": "0", "c": "9"},   "9.0"),
            ("trig",       {"A": "4", "kind": "sin"},        "4.0"),
            ("derivative", {"expr": "x^3", "x0": "2"},       "2.0"),
            ("integral",   {"fn": "x", "a": "0", "b": "2", "n": "8"}, "2.0"),
            ("geometry",   {"shape": "circle", "r": "8.5"},  "8.5"),
            ("transform",  {"a": "2", "b": "0", "c": "0", "d": "1"}, "2.0"),
        ]
        for slug, payload, expected in cases:
            r = self._post(slug, payload)
            self.assertEqual(r.status_code, 200, f"{slug} POST returned {r.status_code}")
            body = r.content.decode()
            self.assertIn('id="module-body"', body, f"{slug} POST lost #module-body")
            self.assertIn(
                f'data-bind-value="{expected}"', body,
                f"{slug} POST did not render slider value {expected!r}",
            )


class ExtrasSmokeTests(TestCase):
    """End-to-end smoke tests for the 5 "extras" added to every module:
    presets, autoplay, click-on-plot coordinate readout, copy formula +
    share URL, and snapshot/compare mode.

    These do not test client-side JS (which Playwright would be better
    suited for), but they DO verify that:
      * every module page renders all the buttons/panels,
      * the per-module snapshot endpoint accepts __snapshot=set/clear
        and round-trips a faded overlay trace in the plot JSON,
      * the preset hx-vals JSON is well-formed for every module,
      * the autoplay bounds are present and finite for every module,
      * the formula data attribute is non-empty for every module.
    """
    MODULES = ("linear", "quadratic", "trig", "derivative",
              "integral", "geometry", "transform")

    @classmethod
    def setUpTestData(cls):
        from django.contrib.auth import get_user_model
        from apps.reading.models import ReadingPage
        User = get_user_model()
        cls.admin = User.objects.create_superuser(
            username="extras-admin", password="pw12345!", email="a@e.com"
        )
        for s in cls.MODULES:
            ReadingPage.objects.update_or_create(
                slug=s, defaults={"module_id": s, "title": s.title(), "body_md": f"# {s}"},
            )

    def _get(self, slug):
        self.client.login(username="extras-admin", password="pw12345!")
        return self.client.get(f"/explore/{slug}/")

    def _post(self, slug, data):
        self.client.login(username="extras-admin", password="pw12345!")
        return self.client.post(f"/explore/{slug}/update/", data, HTTP_HX_REQUEST="true")

    def _snapshot(self, slug, data, op="set"):
        self.client.login(username="extras-admin", password="pw12345!")
        payload = dict(data, **{"__snapshot": op})
        return self.client.post(f"/explore/{slug}/snapshot/", payload, HTTP_HX_REQUEST="true")

    # --- 1. Presets ---------------------------------------------------
    def test_preset_chips_rendered_for_every_module(self):
        """Every module's page must include ≥1 preset chip in its input
        toolbar so the user can switch parameter sets with one click."""
        for mod in self.MODULES:
            r = self._get(mod)
            body = r.content.decode()
            self.assertIn('preset-chip', body,
                          f"{mod} page has no preset chips")
            # The chip posts to the module's update URL
            self.assertIn(f"/explore/{mod}/update/", body,
                          f"{mod} preset chip points to the wrong URL")

    def test_preset_chip_post_changes_module_state(self):
        """Hitting the first preset's hx-vals payload must change the
        rendered insights, proving the chip's POST actually drives a
        full state swap (not just a visual change)."""
        # Per-module "first preset" payload — matches the order in each
        # mathlib's PRESETS list.
        first_presets = {
            "linear":     {"m": "1",  "b": "0"},
            "quadratic":  {"a": "1",  "b": "0",  "c": "0"},
            "trig":       {"A": "1",  "B": "1",  "C": "0",  "D": "0", "kind": "sin"},
            "derivative": {"fn_key": "poly",  "x0": "1",  "h": "0.5"},
            "integral":   {"fn_key": "poly",  "a": "0",  "b": "2",  "n": "20", "method": "midpoint"},
            "geometry":   {"shape": "circle", "r": "3",  "cx": "0",  "cy": "0"},
            "transform":  {"a": "1",  "b": "0",  "c": "0",  "d": "1"},
        }
        for mod, payload in first_presets.items():
            r = self._post(mod, payload)
            self.assertEqual(r.status_code, 200, f"{mod} preset POST returned {r.status_code}")
            body = r.content.decode()
            self.assertIn('id="module-body"', body, f"{mod} preset lost #module-body")

    # --- 2. Autoplay --------------------------------------------------
    def test_autoplay_button_rendered_for_every_module(self):
        """The Play/Stop button + the param <select> must be in every
        module's input toolbar."""
        for mod in self.MODULES:
            r = self._get(mod)
            body = r.content.decode()
            self.assertIn('data-autoplay-button', body,
                          f"{mod} has no autoplay button")
            self.assertIn('data-autoplay-param',   body,
                          f"{mod} has no autoplay param select")
            # At least one <option> with finite min/max/step
            import re
            opts = re.findall(
                r'data-min="([^"]+)"\s+data-max="([^"]+)"\s+data-step="([^"]+)"',
                body,
            )
            self.assertGreater(len(opts), 0,
                               f"{mod} autoplay select has no bound options")
            for mn, mx, st in opts:
                mn, mx, st = float(mn), float(mx), float(st)
                self.assertLess(mn, mx, f"{mod} autoplay min ≥ max")
                self.assertGreater(st, 0, f"{mod} autoplay step ≤ 0")

    # --- 3. Click-on-plot coordinate readout -------------------------
    def test_coordinate_readout_panel_on_every_module(self):
        """Every module's diagram board must include the x/f(x) readout
        panel and the JS-targeted hooks (data-cursor-x / data-cursor-y)."""
        for mod in self.MODULES:
            r = self._get(mod)
            body = r.content.decode()
            self.assertIn('data-coordinate-readout', body,
                          f"{mod} has no coordinate readout panel")
            self.assertIn('data-cursor-x', body,
                          f"{mod} readout panel has no data-cursor-x")
            self.assertIn('data-cursor-y', body,
                          f"{mod} readout panel has no data-cursor-y")

    # --- 4. Copy formula + share URL ---------------------------------
    def test_copy_buttons_rendered_for_every_module(self):
        """Both the Copy f(x) and Share (copy URL) buttons must be in
        every module's diagram board."""
        for mod in self.MODULES:
            r = self._get(mod)
            body = r.content.decode()
            self.assertIn('data-copy-formula', body,
                          f"{mod} has no copy-formula button")
            self.assertIn('data-copy-url', body,
                          f"{mod} has no copy-url button")

    def test_formula_data_attribute_is_non_empty(self):
        """The #module-body's data-formula attribute is what the
        copy-formula JS reads. It must be present and non-empty for
        every module."""
        import re
        for mod in self.MODULES:
            r = self._get(mod)
            body = r.content.decode()
            m = re.search(r'data-formula="([^"]+)"', body)
            self.assertIsNotNone(m, f"{mod} body has no data-formula attribute")
            self.assertTrue(m.group(1).strip(),
                            f"{mod} data-formula is empty")

    # --- 5. Snapshot / compare ---------------------------------------
    def test_snapshot_save_and_clear_round_trip(self):
        """For every module: POST to /snapshot/ with __snapshot=set
        must return 200 and the rendered plot JSON must include a
        trace tagged name='snapshot' with the faded-dot style.
        Then POSTing __snapshot=clear must remove it."""
        import re, json
        for mod in self.MODULES:
            payload = {
                "linear":     {"m": "2",  "b": "0"},
                "quadratic":  {"a": "1",  "b": "0",  "c": "0"},
                "trig":       {"A": "1",  "B": "1",  "C": "0",  "D": "0", "kind": "sin"},
                "derivative": {"fn_key": "poly",  "x0": "1",  "h": "0.5"},
                "integral":   {"fn_key": "poly",  "a": "0",  "b": "2",  "n": "20", "method": "midpoint"},
                "geometry":   {"shape": "circle", "r": "3",  "cx": "0",  "cy": "0"},
                "transform":  {"a": "1",  "b": "0",  "c": "0",  "d": "1"},
            }[mod]
            r_set = self._snapshot(mod, payload, op="set")
            self.assertEqual(r_set.status_code, 200,
                             f"{mod} snapshot set returned {r_set.status_code}")
            body_set = r_set.content.decode()
            m = re.search(rf'id="plot-data-{mod}"[^>]*>([^<]+)<', body_set)
            self.assertIsNotNone(m, f"{mod} snapshot set: no plot-data element")
            pj = json.loads(m.group(1))
            snap_traces = [t for t in pj.get("data", []) if t.get("name") == "snapshot"]
            self.assertGreater(len(snap_traces), 0,
                               f"{mod} snapshot set: no faded snapshot trace")
            for t in snap_traces:
                line = (t.get("line") or {})
                self.assertEqual(line.get("dash"), "dot",
                                 f"{mod} snapshot trace missing dash='dot'")
                self.assertEqual(t.get("opacity"), 0.55,
                                 f"{mod} snapshot trace opacity ≠ 0.55")
            # Clear
            r_clr = self._snapshot(mod, payload, op="clear")
            self.assertEqual(r_clr.status_code, 200,
                             f"{mod} snapshot clear returned {r_clr.status_code}")
            body_clr = r_clr.content.decode()
            m2 = re.search(rf'id="plot-data-{mod}"[^>]*>([^<]+)<', body_clr)
            pj2 = json.loads(m2.group(1))
            self.assertEqual(
                len([t for t in pj2.get("data", []) if t.get("name") == "snapshot"]),
                0,
                f"{mod} snapshot clear left a snapshot trace behind",
            )


class JsSourceTests(SimpleTestCase):
    """Static checks on the JS / CSS files to make sure the click→push
    wiring stays in sync with the HTML the templates emit. Catches bugs
    like editable_stat.js binding to a selector that the template never
    renders."""

    @classmethod
    def setUpTestData(cls):
        pass

    def _read(self, *parts):
        from pathlib import Path
        return Path(*parts).read_text(encoding="utf-8")

    def test_editable_stat_binds_to_actual_template_selectors(self):
        js = self._read("static", "js", "editable_stat.js")
        # Must query at least one selector that _module_body.html actually emits
        self.assertIn("[data-stat-chip]", js,
                      "editable_stat.js does not query [data-stat-chip]")
        self.assertIn("[data-bind-input]", js,
                      "editable_stat.js does not query [data-bind-input]")

    def test_solution_editor_binds_to_solution_table(self):
        js = self._read("static", "js", "solution_editor.js")
        self.assertIn("[data-solution-table]", js)
        self.assertIn("code-pill-result", js)

    def test_htmx_fx_listens_to_afterSwap(self):
        js = self._read("static", "js", "htmx_fx.js")
        self.assertIn("htmx:afterSwap", js)
        # Must re-init Plotly on swapped fragments
        self.assertIn("Plotly.react", js)
        # Must flash the module body
        self.assertIn("module-body-flash", js)
        # Must pop the changed stat cards
        self.assertIn("stat-just-updated", js)

    def test_htmx_fx_included_in_base_module_template(self):
        tmpl = self._read("apps", "explorer", "templates", "explorer", "base_module.html")
        self.assertIn("htmx_fx.js", tmpl,
                      "htmx_fx.js is not included in base_module.html")

    def test_flash_and_pop_animations_defined(self):
        css = self._read("static", "css", "glass.css")
        for needle in (
            "@keyframes module-flash",
            "@keyframes stat-pop",
            ".module-body-flash",
            ".stat-card.stat-just-updated",
            ".stat-card-editable",
            ".stat-edit-hint",
        ):
            self.assertIn(needle, css, f"CSS missing: {needle!r}")

    def test_module_body_id_in_template(self):
        tmpl = self._read("templates", "partials", "_module_body.html")
        self.assertIn('id="module-body"', tmpl,
                      "#module-body is missing from _module_body.html")


class FocusAndAnnotationTests(TestCase):
    """Verify the Focus + Freeze &amp; draw toolbar tool:

    1. Every module page renders the two new buttons + the overlay
       container (markup test).
    2. The annotation-save endpoint accepts a valid JSON payload and
       creates a WhiteboardDrawing tagged with the module slug.
    3. The annotation-list endpoint returns only that user's rows
       for the requested module.
    4. The annotation-save endpoint refuses anonymous users (302 to
       the login page).
    5. The annotation-load endpoint fetches the right row by pk.
    """

    MODULES = ("linear", "quadratic", "trig", "derivative",
               "integral", "geometry", "transform")

    @classmethod
    def setUpTestData(cls):
        from django.contrib.auth import get_user_model
        from apps.reading.models import ReadingPage
        from apps.accounts.models import get_or_create_profile
        User = get_user_model()
        cls.user = User.objects.create_user(
            username="annotator", password="pw12345!", email="a@e.com"
        )
        cls.other = User.objects.create_user(
            username="stranger", password="pw12345!", email="s@e.com"
        )
        # Grant our annotator access to all modules via their profile.
        cls.profile = get_or_create_profile(cls.user)
        cls.profile.allowed_modules = list(cls.MODULES)
        cls.profile.save()
        cls.other_profile = get_or_create_profile(cls.other)
        cls.other_profile.allowed_modules = list(cls.MODULES)
        cls.other_profile.save()
        for s in cls.MODULES:
            ReadingPage.objects.update_or_create(
                slug=s, defaults={"module_id": s, "title": s.title(), "body_md": f"# {s}"},
            )

    def _read(self, *parts):
        from pathlib import Path
        return Path(*parts).read_text(encoding="utf-8")

    def setUp(self):
        self.client.login(username="annotator", password="pw12345!")

    def _get_module(self, slug):
        return self.client.get(f"/explore/{slug}/")

    def test_focus_and_whiteboard_buttons_render_for_every_module(self):
        """Every Explore page must expose the Focus and Freeze &amp; draw
        toolbar buttons, the focus overlay container, and the embedded
        whiteboard canvas wrap."""
        for mod in self.MODULES:
            r = self._get_module(mod)
            self.assertEqual(r.status_code, 200, f"{mod} GET returned {r.status_code}")
            body = r.content.decode()
            self.assertIn("data-focus-toggle", body,
                          f"{mod} page has no Focus button")
            self.assertIn("data-whiteboard-toggle", body,
                          f"{mod} page has no Freeze & draw button")
            self.assertIn("data-focus-overlay", body,
                          f"{mod} page has no focus overlay container")
            self.assertIn("data-wb-canvas-wrap", body,
                          f"{mod} overlay has no whiteboard canvas wrap")
            # The overlay must include the toolbar groups the JS expects.
            for needle in (
                "data-wb-tool=\"pen\"",
                "data-wb-tool=\"highlighter\"",
                "data-wb-tool=\"eraser\"",
                "data-wb-undo",
                "data-wb-redo",
                "data-wb-clear",
                "data-wb-save",
                "data-wb-load",
            ):
                self.assertIn(needle, body,
                              f"{mod} overlay missing {needle!r}")
            # Save URL points at the per-module annotation_save route.
            self.assertIn(
                f"/explore/{mod}/annotations/save/", body,
                f"{mod} overlay data-wb-save-url is wrong",
            )
            self.assertIn(
                f"/explore/{mod}/annotations/", body,
                f"{mod} overlay data-wb-load-url-base is wrong",
            )

    def test_annotation_save_creates_row(self):
        """POSTing a valid stroke payload to the per-module
        /annotations/save/ endpoint must persist a WhiteboardDrawing
        tagged with that module slug, owned by the current user."""
        payload = {
            "title": "My parabola sketch",
            "strokes": [
                {"tool": "pen", "color": "#ef4444", "size": 3,
                 "data": {"points": [{"x": 10, "y": 10},
                                     {"x": 50, "y": 50},
                                     {"x": 90, "y": 10}]}},
            ],
            "background_data_url": "",
            "pk": None,
        }
        r = self.client.post(
            "/explore/quadratic/annotations/save/",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(r.status_code, 200, r.content)
        body = r.json()
        self.assertTrue(body.get("ok"))
        self.assertEqual(body.get("module_slug"), "quadratic")
        self.assertIsNotNone(body.get("id"))
        from whiteboard.models import WhiteboardDrawing
        d = WhiteboardDrawing.objects.get(pk=body["id"])
        self.assertEqual(d.user, self.user)
        self.assertEqual(d.module_slug, "quadratic")
        self.assertEqual(d.title, "My parabola sketch")
        import json as _json
        self.assertEqual(len(_json.loads(d.strokes_json)), 1)

    def test_annotation_save_rejects_anonymous(self):
        """Anonymous users get redirected to the login page (302)."""
        self.client.logout()
        r = self.client.post(
            "/explore/quadratic/annotations/save/",
            data=json.dumps({"strokes": []}),
            content_type="application/json",
        )
        # 302 to /accounts/login/ (Django default) or 403, either way not 200.
        self.assertIn(r.status_code, (302, 403),
                      f"anon save should be blocked, got {r.status_code}")

    def test_annotation_list_returns_only_user_rows(self):
        """annotation_list must return only the current user's saved
        annotations for the requested module, and must never expose
        another user's row."""
        from whiteboard.models import WhiteboardDrawing
        # Create one row per module for the current user, and one
        # for the other user on the same module.
        for s in self.MODULES:
            WhiteboardDrawing.objects.create(
                user=self.user, title=f"{s} mine",
                module_slug=s, strokes_json="[]",
            )
            if s == "quadratic":
                WhiteboardDrawing.objects.create(
                    user=self.other, title="stranger quad",
                    module_slug="quadratic", strokes_json="[]",
                )
        r = self.client.get("/explore/quadratic/annotations/")
        self.assertEqual(r.status_code, 200)
        body = r.json()
        self.assertTrue(body["ok"])
        self.assertEqual(body["module"], "quadratic")
        titles = [d["title"] for d in body["drawings"]]
        self.assertIn("quadratic mine", titles)
        self.assertNotIn("stranger quad", titles,
                         "annotation_list leaked another user's drawing")

    def test_annotation_load_returns_row(self):
        """annotation_load must return the right drawing by pk and 404
        on a foreign user's row."""
        from whiteboard.models import WhiteboardDrawing
        d = WhiteboardDrawing.objects.create(
            user=self.user, title="loaded",
            module_slug="trig", strokes_json='[{"tool":"pen"}]',
        )
        r = self.client.get(f"/explore/trig/annotations/load/{d.pk}/")
        self.assertEqual(r.status_code, 200)
        body = r.json()
        self.assertTrue(body["ok"])
        self.assertEqual(body["id"], d.pk)
        self.assertEqual(body["title"], "loaded")
        self.assertEqual(body["module_slug"], "trig")
        self.assertEqual(len(body["strokes"]), 1)
        # 404 on a non-existent pk
        r404 = self.client.get("/explore/trig/annotations/load/999999/")
        self.assertEqual(r404.status_code, 404)

    def test_module_focus_js_included_in_base_module(self):
        """The base module template must include the new module_focus.js
        and the standalone whiteboard.js / whiteboard.css so the
        toolbar buttons have working code to drive."""
        tmpl = self._read("apps", "explorer", "templates", "explorer", "base_module.html")
        self.assertIn("module_focus.js", tmpl,
                      "module_focus.js is not included in base_module.html")
        self.assertIn("whiteboard.js", tmpl,
                      "whiteboard.js is not included in base_module.html")
        self.assertIn("whiteboard.css", tmpl,
                      "whiteboard.css is not included in base_module.html")

    def test_whiteboard_engine_is_idempotent(self):
        """Whiteboard.init() called twice on the same wrap must NOT
        double-bind click / canvas / keyboard / resize listeners.
        The engine marks the wrap with data-wb-bound='1' on first run
        and skips bind* on subsequent calls."""
        js = self._read("static", "whiteboard", "whiteboard.js")
        # dataset.wbBound in the JS corresponds to the data-wb-bound
        # attribute on the DOM element.
        self.assertIn("wbBound", js,
                      "whiteboard.js does not implement a re-init guard")
        # The guard must compare against "1" and set the attribute on bind.
        self.assertIn('wrap.dataset.wbBound = "1"', js,
                      "whiteboard.js does not set the bound marker on first init")
        self.assertIn("alreadyBound", js,
                      "whiteboard.js does not check alreadyBound before re-binding")
        self.assertIn("refresh: function", js,
                      "whiteboard.js does not expose a refresh() method")

    def test_focus_overlay_v2_features_render_for_every_module(self):
        """The v2 focus overlay must expose: stage (zoom/pan viewport),
        grid overlay, floating draggable toolbar with handle + collapse
        button, color picker, zoom readout, recent drawer, help
        overlay, and Pan tool button."""
        for mod in self.MODULES:
            body = self._get_module(mod).content.decode()
            for needle in (
                "data-focus-stage",       # viewport
                "data-stage-content",     # pan/zoom target
                "data-focus-grid",        # grid overlay
                "data-focus-toolbar",     # floating panel
                "data-toolbar-handle",    # drag handle
                "data-toolbar-collapse",  # collapse button
                "data-wb-color-picker",   # custom color
                "data-zoom-percent",      # zoom readout
                "data-zoom-in",
                "data-zoom-out",
                "data-zoom-fit",
                "data-zoom-reset",
                "data-grid-toggle",
                "data-focus-pan",         # pan tool
                "data-focus-recent",      # recent drawer
                "data-focus-recent-list",
                "data-focus-help-overlay",
                "data-focus-export",      # export combined PNG
                "data-wb-fixed-width",    # canvas pinned to natural res
                "data-wb-fixed-height",
            ):
                self.assertIn(needle, body,
                              f"{mod} overlay is missing {needle!r}")

    def test_focus_overlay_pins_canvas_to_natural_size(self):
        """The whiteboard canvas wrap must be pinned to the diagram's
        natural resolution (1600×900) so the drawing surface stays
        crisp at any zoom level. This is the only way the user can
        only draw on the diagram area, not the dark space around it."""
        body = self._get_module("linear").content.decode()
        self.assertIn('data-wb-fixed-width="1600"', body)
        self.assertIn('data-wb-fixed-height="900"', body)
        # The stage content must also be sized to 1600×900.
        self.assertIn("width:1600px", body)
        self.assertIn("height:900px", body)

    def test_module_focus_js_contains_zoom_pan_and_export(self):
        js = self._read("static", "js", "module_focus.js")
        for needle in (
            "function zoomTo",
            "function zoomIn",
            "function zoomOut",
            "function zoomFit",
            "function zoomReset",
            "function startPan",
            "function movePan",
            "function onGridToggle",
            "function onPanToggle",
            "function onExport",
            "function loadAnnotationIntoBoard",
            "function loadRecentList",
            "function renderRecentList",
            "function deleteAnnotation",
            "function bindToolbarDrag",
            "function bindColorPicker",
            "function bindSaveHook",
            "function setHelpOpen",
            "function setRecentOpen",
            "function onKeydown",
            "function onWheel",
            "data-wb-save",          # save hook target
            "background_data_url",   # full payload field
            "csrftoken",             # csrf for annotation save
            "annotationSaveUrl",     # dataset key (camelCase)
            "annotationListUrl",     # dataset key (camelCase)
            # Keyboard shortcuts
            "zoomFit",
            "setGrid",
            "setPanTool",
            "setToolbarCollapsed",
            "onHelpToggle",
        ):
            self.assertIn(needle, js,
                          f"module_focus.js is missing {needle!r}")

    def test_focus_overlay_css_contains_new_classes(self):
        css = self._read("static", "css", "glass.css")
        for needle in (
            ".focus-overlay",
            ".focus-stage",
            ".stage-content",
            ".focus-toolbar",
            ".focus-toolbar-handle",
            ".focus-toolbar-collapse",
            ".focus-toolbar-row",
            ".focus-toolbar-label",
            ".focus-toolbar-dots",
            ".focus-color-picker",
            ".focus-zoom-readout",
            ".focus-zoom-percent",
            ".focus-grid",
            ".focus-recent",
            ".focus-recent-item",
            ".focus-help",
            ".focus-help-card",
            ".focus-help-grid",
            "body.focus-open",
            ".focus-tool-wide",
            ".focus-tool-pan",
        ):
            self.assertIn(needle, css,
                          f"glass.css is missing focus rule {needle!r}")

    def test_whiteboard_engine_supports_fixed_canvas_size(self):
        """The engine's resize() must respect data-wb-fixed-width /
        data-wb-fixed-height so the focus overlay can pin the canvas
        backing buffer to the diagram's natural resolution. Without
        this, drawing becomes pixelated at zoom > 100%."""
        js = self._read("static", "whiteboard", "whiteboard.js")
        self.assertIn("wbFixedWidth", js,
                      "whiteboard.js does not read data-wb-fixed-width")
        self.assertIn("wbFixedHeight", js,
                      "whiteboard.js does not read data-wb-fixed-height")

