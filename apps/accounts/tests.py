from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.test import TestCase

from apps.accounts.models import ALL_MODULES, UserProfile


User = get_user_model()


class ProfileTests(TestCase):
    def test_profile_auto_created(self):
        u = User.objects.create_user(username="alice", password="pw12345!")
        self.assertTrue(hasattr(u, "userprofile"))
        self.assertEqual(u.userprofile.role, "student")
        self.assertEqual(u.userprofile.allowed_modules, [])

    def test_superuser_becomes_admin(self):
        u = User.objects.create_superuser(username="root", password="pw12345!", email="r@e.com")
        self.assertEqual(u.userprofile.role, "admin")
        self.assertEqual(set(u.userprofile.allowed_modules), set(ALL_MODULES))

    def test_module_access(self):
        u = User.objects.create_user(username="bob", password="pw12345!")
        u.userprofile.allowed_modules = ["linear"]
        u.userprofile.save()
        self.assertTrue(u.userprofile.has_module_access("linear"))
        self.assertFalse(u.userprofile.has_module_access("geometry"))

    def test_admin_access_to_everything(self):
        u = User.objects.create_user(username="admin2", password="pw12345!")
        u.userprofile.role = "admin"
        u.userprofile.save()
        self.assertTrue(u.userprofile.has_module_access("integral"))


class RoleDecoratorTests(TestCase):
    def setUp(self):
        from apps.accounts.decorators import role_required
        self._role_required = role_required

    def test_role_required_blocks_student(self):
        decorated = self._role_required("teacher")(lambda r: "ok")
        student = User.objects.create_user(username="s1", password="pw12345!")
        from django.test import RequestFactory
        rf = RequestFactory()
        req = rf.get("/")
        req.user = student
        with self.assertRaises(PermissionDenied):
            decorated(req)

    def test_role_required_allows_teacher(self):
        decorated = self._role_required("teacher")(lambda r: "ok")
        teacher = User.objects.create_user(username="t1", password="pw12345!")
        teacher.userprofile.role = "teacher"
        teacher.userprofile.save()
        from django.test import RequestFactory
        rf = RequestFactory()
        req = rf.get("/")
        req.user = teacher
        self.assertEqual(decorated(req), "ok")
