"""Backfill UserProfile rows for any user that doesn't have one.

The post_save signal normally creates a profile when a User is created,
but users added before that signal existed (or imported via fixtures /
raw SQL) will be missing one. Run this once after upgrading:

    python manage.py ensure_profiles

It's idempotent — users that already have a profile are left alone.
"""
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from apps.accounts.models import UserProfile, get_or_create_profile


class Command(BaseCommand):
    help = "Create a UserProfile for every user that is missing one."

    def handle(self, *args, **options):
        User = get_user_model()
        created, fixed = 0, 0
        for user in User.objects.all():
            try:
                _ = user.userprofile  # noqa: F841
            except UserProfile.DoesNotExist:
                get_or_create_profile(user)
                created += 1
        total = User.objects.count()
        with_profile = UserProfile.objects.count()
        self.stdout.write(
            f"users={total} profiles={with_profile} created={created}"
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"Backfilled {created} missing profile(s)."))
        else:
            self.stdout.write("All users already have a profile.")
