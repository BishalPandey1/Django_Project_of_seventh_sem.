from django.db import models

from apps.accounts.models import MODULE_CHOICES


class ReadingPage(models.Model):
    slug = models.SlugField(unique=True)
    module_id = models.CharField(max_length=32, choices=MODULE_CHOICES, blank=True)
    title = models.CharField(max_length=200)
    body_md = models.TextField(help_text="Markdown body")
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ["order", "title"]

    def __str__(self):
        return self.title
