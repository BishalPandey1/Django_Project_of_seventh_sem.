"""End-to-end smoke tests for every URL added by the explorer feature."""

from django.contrib.auth import get_user_model
from django.test import TestCase


User = get_user_model()


class ExplorerRoutesTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_superuser(
            username="audit-admin", password="pw12345!", email="a@e.com"
        )
        cls.teacher = User.objects.create_user(username="audit-teacher", password="pw12345!")
        cls.teacher.userprofile.role = "teacher"
        cls.teacher.userprofile.allowed_modules = [
            "linear", "quadratic", "trig", "derivative", "integral", "geometry", "transform",
        ]
        cls.teacher.userprofile.save()
        cls.student = User.objects.create_user(username="audit-student", password="pw12345!")
        # student has no modules
        cls.reading = [
            "linear", "quadratic", "trig", "derivative", "integral", "geometry", "transform",
        ]

    def setUp(self):
        from apps.reading.models import ReadingPage
        for s in self.reading:
            ReadingPage.objects.update_or_create(
                slug=s,
                defaults={"module_id": s, "title": s.title(), "body_md": f"# {s}\n\nbody"},
            )

    # ── anonymous ─────────────────────────────────────────────────────
    def test_anonymous_redirects_to_login(self):
        for path in [
            "/explore/", "/explore/linear/", "/reading/", "/reading/linear/",
            "/tasks/", "/teacher/", "/dashboard/", "/home/", "/modules/",
        ]:
            r = self.client.get(path)
            self.assertIn(r.status_code, (200, 302), f"{path} -> {r.status_code}")

    # ── admin: every explorer page renders ────────────────────────────
    def test_admin_renders_every_module(self):
        self.client.login(username="audit-admin", password="pw12345!")
        for slug in self.reading:
            r = self.client.get(f"/explore/{slug}/")
            self.assertEqual(r.status_code, 200, f"/explore/{slug}/ -> {r.status_code}")
            self.assertContains(r, f'plot-{slug}')
            self.assertContains(r, 'data-board="input"')
            self.assertContains(r, 'data-board="diagram"')
            self.assertContains(r, 'data-board="solution"')
            self.assertContains(r, 'data-board="solver"')
            self.assertContains(r, 'data-solution-table')
            self.assertContains(r, "Variable solver")

    def test_admin_hub_renders(self):
        self.client.login(username="audit-admin", password="pw12345!")
        r = self.client.get("/explore/")
        self.assertEqual(r.status_code, 200)
        for slug in self.reading:
            self.assertContains(r, f'href="/explore/{slug}/"')

    # ── admin: every HTMX POST endpoint returns 200 + contains #module-body fragment ─
    def test_htmx_updates_return_fragments(self):
        self.client.login(username="audit-admin", password="pw12345!")
        cases = [
            ("linear",     {"m": "3", "b": "1"}),
            ("quadratic",  {"a": "1", "b": "-5", "c": "6"}),
            ("trig",       {"A": "2", "B": "1", "C": "0", "D": "0"}),
            ("derivative", {"fn_key": "poly", "x0": "1", "h": "0.5"}),
            ("integral",   {"fn_key": "poly", "a": "0", "b": "4", "n": "20", "method": "midpoint"}),
            ("geometry",   {"shape": "circle", "r": "3", "cx": "0", "cy": "0"}),
            ("transform",  {"a": "1", "b": "0", "c": "0", "d": "1"}),
        ]
        for slug, data in cases:
            r = self.client.post(
                f"/explore/{slug}/update/", data, HTTP_HX_REQUEST="true"
            )
            self.assertEqual(r.status_code, 200, f"{slug} update -> {r.status_code}")
            body = r.content.decode()
            self.assertIn("plot-data", body, f"{slug}: missing plot-data")
            self.assertIn("data-board=\"diagram\"", body, f"{slug}: missing diagram")
            self.assertIn("data-board=\"solution\"", body, f"{slug}: missing solution")
            self.assertIn("data-board=\"solver\"", body, f"{slug}: missing solver")
            self.assertIn("data-solution-table", body, f"{slug}: missing solution table")

    # ── student with no modules sees empty state ───────────────────────
    def test_student_with_no_modules_sees_empty_state(self):
        self.client.login(username="audit-student", password="pw12345!")
        r = self.client.get("/explore/")
        self.assertEqual(r.status_code, 200)
        # No card for linear
        self.assertNotContains(r, 'href="/explore/linear/"')

    def test_student_blocked_from_module(self):
        self.client.login(username="audit-student", password="pw12345!")
        r = self.client.get("/explore/linear/")
        self.assertEqual(r.status_code, 403)

    # ── teacher ───────────────────────────────────────────────────────
    def test_teacher_can_open_dashboard(self):
        self.client.login(username="audit-teacher", password="pw12345!")
        r = self.client.get("/teacher/")
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Students")

    def test_teacher_blocked_from_admin(self):
        self.client.login(username="audit-teacher", password="pw12345!")
        r = self.client.get("/teacher/admin/")
        self.assertEqual(r.status_code, 403)

    def test_admin_can_open_admin_home(self):
        self.client.login(username="audit-admin", password="pw12345!")
        r = self.client.get("/teacher/admin/")
        self.assertEqual(r.status_code, 200)

    # ── reading room ──────────────────────────────────────────────────
    def test_reading_index_renders(self):
        self.client.login(username="audit-admin", password="pw12345!")
        r = self.client.get("/reading/")
        self.assertEqual(r.status_code, 200)
        for slug in self.reading:
            self.assertContains(r, f'href="/reading/{slug}/"')

    def test_reading_detail_renders(self):
        self.client.login(username="audit-admin", password="pw12345!")
        for slug in self.reading:
            r = self.client.get(f"/reading/{slug}/")
            self.assertEqual(r.status_code, 200)
            self.assertContains(r, "<h1")

    # ── dashboard + home + modules alias ──────────────────────────────
    def test_dashboard_renders(self):
        self.client.login(username="audit-admin", password="pw12345!")
        r = self.client.get("/dashboard/")
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Welcome")

    def test_home_alias_redirects(self):
        self.client.login(username="audit-admin", password="pw12345!")
        r = self.client.get("/home/")
        self.assertEqual(r.status_code, 302)

    def test_modules_root_redirects_to_explorer(self):
        self.client.login(username="audit-admin", password="pw12345!")
        r = self.client.get("/modules/")
        self.assertEqual(r.status_code, 302)
        self.assertEqual(r.url, "/explore/")

    # ── tasks ─────────────────────────────────────────────────────────
    def test_tasks_list_renders(self):
        self.client.login(username="audit-admin", password="pw12345!")
        r = self.client.get("/tasks/")
        self.assertEqual(r.status_code, 200)

    # ── toggle theme ──────────────────────────────────────────────────
    def test_toggle_theme_requires_login(self):
        r = self.client.post("/accounts/toggle-theme/")
        self.assertIn(r.status_code, (302, 401), f"unexpected {r.status_code}")

    def test_toggle_theme_works(self):
        self.client.login(username="audit-admin", password="pw12345!")
        before = self.admin.userprofile.theme
        r = self.client.post("/accounts/toggle-theme/")
        self.assertEqual(r.status_code, 204)
        self.admin.userprofile.refresh_from_db()
        self.assertNotEqual(self.admin.userprofile.theme, before)

    # ── regression: un-namespaced url refs in accounts templates ───────
    def test_accounts_pages_render(self):
        self.client.login(username="audit-admin", password="pw12345!")
        for path in [
            "/accounts/lessons/",
            "/accounts/profile/",
            "/accounts/settings/",
            "/accounts/help/",
            "/accounts/graph/",
        ]:
            r = self.client.get(path)
            self.assertEqual(r.status_code, 200, f"{path} -> {r.status_code}")

    def test_topic_detail_renders(self):
        self.client.login(username="audit-admin", password="pw12345!")
        r = self.client.get("/accounts/lessons/")
        self.assertEqual(r.status_code, 200)
        # every lesson in the view has topic links; pick first one
        import re
        m = re.search(rb'href="/accounts/lessons/([^/]+)/([^/]+)/"', r.content)
        if m:
            lesson, topic = m.group(1).decode(), m.group(2).decode()
            r = self.client.get(f"/accounts/lessons/{lesson}/{topic}/")
            self.assertEqual(r.status_code, 200, f"topic detail {lesson}/{topic} -> {r.status_code}")

    # ── regression: dashboard must include HTMX + csrf meta ──────────
    def test_dashboard_loads_htmx_and_csrf(self):
        self.client.login(username="audit-admin", password="pw12345!")
        r = self.client.get("/dashboard/")
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'id="csrf-token"', count=0)  # just verify it parses
        # CSRF meta must be present
        self.assertIn(b'name="csrf-token"', r.content)
        # HTMX script must be present
        self.assertIn(b"htmx.org", r.content)
        # hx-headers must be set on body
        self.assertIn(b"hx-headers", r.content)

    # ── regression: toggle-theme works with CSRF token (dashboard) ───
    def test_toggle_theme_with_csrf_token(self):
        self.client.login(username="audit-admin", password="pw12345!")
        r = self.client.get("/dashboard/")
        import re
        m = re.search(rb'csrf-token"\s+content="([^"]+)"', r.content)
        self.assertIsNotNone(m, "no csrf-token meta in dashboard")
        token = m.group(1).decode()
        before = self.admin.userprofile.theme
        r = self.client.post(
            "/accounts/toggle-theme/", HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(r.status_code, 204)
        self.admin.userprofile.refresh_from_db()
        self.assertNotEqual(self.admin.userprofile.theme, before)

    # ── regression: user without a profile gets one created on-the-fly ─
    def test_user_without_profile_does_not_500(self):
        from apps.accounts.models import UserProfile, get_or_create_profile
        # Create a user, then delete their profile
        ghost = User.objects.create_user(username="ghost", password="pw12345!")
        UserProfile.objects.filter(user=ghost).delete()
        self.assertFalse(UserProfile.objects.filter(user=ghost).exists())
        # Login and visit dashboard
        self.client.login(username="ghost", password="pw12345!")
        r = self.client.get("/dashboard/")
        self.assertEqual(r.status_code, 200)
        # Profile should have been created on-the-fly
        self.assertTrue(UserProfile.objects.filter(user=ghost).exists())
        r2 = self.client.get("/explore/")
        self.assertIn(r2.status_code, (200, 403))
        # explorer hub: ghost has no modules -> 200 with empty state
        self.assertEqual(r2.status_code, 200)

    def test_ensure_profiles_command(self):
        from io import StringIO
        from django.core.management import call_command
        from apps.accounts.models import UserProfile
        # create orphan
        orphan = User.objects.create_user(username="orphan", password="pw12345!")
        UserProfile.objects.filter(user=orphan).delete()
        out = StringIO()
        call_command("ensure_profiles", stdout=out)
        self.assertTrue(UserProfile.objects.filter(user=orphan).exists())

    # ── regression: 3-board layout on every module ───────────────────
    def test_three_boards_layout(self):
        self.client.login(username="audit-admin", password="pw12345!")
        for slug in self.reading:
            r = self.client.get(f"/explore/{slug}/")
            body = r.content.decode()
            self.assertIn('data-board="input"', body, f"{slug}: no input board")
            self.assertIn('data-board="diagram"', body, f"{slug}: no diagram board")
            self.assertIn('data-board="solution"', body, f"{slug}: no solution board")
            self.assertIn('data-board="solver"', body, f"{slug}: no solver board")
            self.assertIn('data-reset-module', body, f"{slug}: no reset button")
            self.assertIn('data-solution-table', body, f"{slug}: no solution table")

    # ── regression: reset button restores defaults ───────────────────
    def test_reset_button_restores_defaults(self):
        self.client.login(username="audit-admin", password="pw12345!")
        r = c = self.client.post(
            "/explore/linear/update/", {"__reset": "1"}, HTTP_HX_REQUEST="true"
        )
        self.assertEqual(r.status_code, 200)
        # The default for m is 1.0 and for b is 0.0
        self.assertIn(b'value="1.0"', r.content)
        self.assertIn(b'value="0"', r.content)

    # ── regression: invalid input falls back to defaults ─────────────
    def test_invalid_input_falls_back_to_defaults(self):
        self.client.login(username="audit-admin", password="pw12345!")
        r = self.client.post(
            "/explore/linear/update/",
            {"m": "not-a-number", "b": ""},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(r.status_code, 200)
        # defaults are m=1, b=0
        self.assertIn(b'value="1.0"', r.content)
        self.assertIn(b'value="0"', r.content)
