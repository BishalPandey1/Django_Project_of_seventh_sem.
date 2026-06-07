from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.accounts.models import MODULE_CHOICES


class Task(models.Model):
    module_id = models.CharField(max_length=32, choices=MODULE_CHOICES, blank=True)
    title = models.CharField(max_length=200)
    problem = models.TextField()
    due_date = models.DateField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_tasks",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def is_overdue(self):
        return self.due_date < timezone.now().date()

    def __str__(self):
        return self.title


class Submission(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="submissions")
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="submissions",
    )
    answer = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed = models.BooleanField(default=False)
    score = models.IntegerField(null=True, blank=True)
    feedback = models.TextField(blank=True)

    class Meta:
        unique_together = [("task", "student")]

    def __str__(self):
        return f"{self.student} → {self.task}"
