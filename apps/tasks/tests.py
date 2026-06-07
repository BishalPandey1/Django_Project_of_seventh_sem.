from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from apps.tasks.models import Submission, Task


User = get_user_model()


class TaskTests(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(username="t1", password="pw12345!")
        self.teacher.userprofile.role = "teacher"
        self.teacher.userprofile.save()
        self.student = User.objects.create_user(username="s1", password="pw12345!")
        self.today = timezone.now().date()

    def test_create_task(self):
        t = Task.objects.create(
            module_id="linear",
            title="T1",
            problem="...",
            due_date=self.today + timedelta(days=2),
            created_by=self.teacher,
        )
        self.assertEqual(str(t), "T1")

    def test_overdue(self):
        t = Task.objects.create(
            module_id="linear", title="Old", problem="...",
            due_date=self.today - timedelta(days=1), created_by=self.teacher,
        )
        self.assertTrue(t.is_overdue())
        t2 = Task.objects.create(
            module_id="linear", title="New", problem="...",
            due_date=self.today + timedelta(days=1), created_by=self.teacher,
        )
        self.assertFalse(t2.is_overdue())

    def test_submission_unique(self):
        t = Task.objects.create(
            module_id="linear", title="T", problem="...",
            due_date=self.today, created_by=self.teacher,
        )
        Submission.objects.create(task=t, student=self.student, answer="a")
        with self.assertRaises(Exception):
            Submission.objects.create(task=t, student=self.student, answer="b")
