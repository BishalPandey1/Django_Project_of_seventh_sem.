"""Seed demo accounts, tasks, and reading pages."""

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.accounts.models import ALL_MODULES
from apps.reading.models import ReadingPage


User = get_user_model()


class Command(BaseCommand):
    help = "Create demo users, tasks, and reading pages."

    def handle(self, *args, **options):
        # admin
        admin, created = User.objects.get_or_create(
            username="admin",
            defaults={"email": "admin@example.com", "is_staff": True, "is_superuser": True},
        )
        if created:
            admin.set_password("admin12345")
            admin.save()
        elif not admin.is_superuser:
            admin.is_superuser = True
            admin.is_staff = True
            admin.save()

        # teachers
        for i in (1, 2):
            u, created = User.objects.get_or_create(
                username=f"teacher{i}",
                defaults={"email": f"teacher{i}@example.com"},
            )
            if created:
                u.set_password("teach12345")
                u.save()
            profile = u.userprofile
            profile.role = "teacher"
            profile.allowed_modules = ALL_MODULES
            profile.save()

        # students
        for i in range(1, 6):
            u, created = User.objects.get_or_create(
                username=f"student{i}",
                defaults={"email": f"student{i}@example.com"},
            )
            if created:
                u.set_password("study12345")
                u.save()
            profile = u.userprofile
            profile.role = "student"
            if not profile.allowed_modules:
                profile.allowed_modules = []
            profile.save()

        # tasks (3 across modules)
        from apps.tasks.models import Task
        today = timezone.now().date()
        for slug, title in [
            ("linear",    "Slope practice"),
            ("quadratic", "Vertex hunt"),
            ("integral",  "Riemann-sum estimate"),
        ]:
            Task.objects.get_or_create(
                title=title,
                defaults={
                    "module_id": slug,
                    "problem": f"Practice problem for the {slug} module.",
                    "due_date": today + timedelta(days=7),
                    "created_by": admin,
                },
            )

        # reading pages (idempotent — same as seed_reading)
        from apps.reading.management.commands.seed_reading import PAGES
        for order, (slug, title, body) in enumerate(PAGES):
            ReadingPage.objects.update_or_create(
                slug=slug,
                defaults={"module_id": slug, "title": title, "body_md": body.strip(), "order": order},
            )

        self.stdout.write(self.style.SUCCESS(
            "Demo data created. Login as admin/admin12345 to begin."
        ))
