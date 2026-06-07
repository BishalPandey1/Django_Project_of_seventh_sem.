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
    # Module annotations (from the Explore visualizers) are tagged with
    # the module slug so they can be listed/loaded per module. Standalone
    # whiteboard drawings leave this empty.
    module_slug = models.CharField(max_length=32, blank=True, default="")
    # JSON-encoded stroke list (the existing PNG path stays for the
    # standalone whiteboard). Module annotations are stored as JSON so
    # they re-render at any resolution and can be re-edited.
    strokes_json = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        indexes = [
            models.Index(fields=["user", "module_slug", "-updated_at"]),
        ]

    def __str__(self):
        return f"{self.title} ({self.user})"
