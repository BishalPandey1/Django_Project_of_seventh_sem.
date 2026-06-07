from django.conf import settings
from django.db import models


class WhiteboardDrawing(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="whiteboard_drawings",
    )
    title = models.CharField(max_length=120, default="Untitled")
    image = models.ImageField(upload_to="whiteboard/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.title} ({self.user})"
