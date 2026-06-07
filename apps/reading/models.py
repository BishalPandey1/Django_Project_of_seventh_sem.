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

    # ── Derived display helpers ───────────────────────────────────────
    @property
    def word_count(self) -> int:
        return len((self.body_md or "").split())

    @property
    def reading_minutes(self) -> int:
        # ~220 words per minute — comfortable for technical prose.
        return max(1, round(self.word_count / 220))

    @property
    def chapter_number(self) -> int:
        return (self.order or 0) + 1

    @property
    def excerpt(self) -> str:
        """Return the first prose paragraph of the article (markdown stripped).

        Falls back to the first 240 characters if no paragraph is found.
        Used for preview cards so the user gets a taste of the chapter.
        """
        if not self.body_md:
            return ""
        lines = self.body_md.strip().splitlines()
        buf: list[str] = []
        for ln in lines:
            s = ln.strip()
            if not s:
                if buf:
                    break
                continue
            if s.startswith("#"):
                continue
            buf.append(s)
        text = " ".join(buf) if buf else self.body_md.strip()
        if len(text) <= 260:
            return text
        cut = text[:260].rsplit(" ", 1)[0]
        return cut + "…"

    @property
    def key_ideas(self) -> list[str]:
        """Pull the first few bullet items from the article — shown on cards."""
        if not self.body_md:
            return []
        ideas: list[str] = []
        for ln in self.body_md.splitlines():
            s = ln.strip()
            if not s:
                if ideas:
                    break
                continue
            if s.startswith(("- ", "* ")):
                idea = s[2:].strip()
                # drop leading **bold:** prefix
                if idea.startswith("**"):
                    end = idea.find("**", 2)
                    if end > 0:
                        idea = idea[end + 2:].lstrip(" :")
                ideas.append(idea)
                if len(ideas) >= 3:
                    break
            elif s.startswith("#") and ideas:
                break
        return ideas

    @property
    def accent_color(self) -> str:
        """Map each module to a brand colour used throughout the reading UI."""
        return {
            "linear":    "#3b82f6",
            "quadratic": "#a855f7",
            "trig":      "#06b6d4",
            "derivative":"#f97316",
            "integral":  "#10b981",
            "geometry":  "#ec4899",
            "transform": "#f59e0b",
        }.get(self.module_id, "#6366f1")
