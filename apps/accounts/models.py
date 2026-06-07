"""User-profile model, role-based access, and the post-save signal."""

from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


MODULE_CHOICES = [
    ("linear", "Linear Functions"),
    ("quadratic", "Quadratics"),
    ("trig", "Sine Waves"),
    ("derivative", "Derivatives"),
    ("integral", "Integrals"),
    ("geometry", "Geometry"),
    ("transform", "Linear Transforms"),
]

ALL_MODULES = [m[0] for m in MODULE_CHOICES]


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="userprofile",
    )
    role = models.CharField(
        max_length=16,
        choices=[("student", "Student"), ("teacher", "Teacher"), ("admin", "Admin")],
        default="student",
    )
    allowed_modules = models.JSONField(default=list, blank=True)
    visited_modules = models.JSONField(default=list, blank=True)
    theme = models.CharField(
        max_length=8,
        choices=[("light", "Light"), ("dark", "Dark")],
        default="light",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def has_module_access(self, module_id: str) -> bool:
        if self.role == "admin" or self.user.is_superuser:
            return True
        return module_id in (self.allowed_modules or [])

    def __str__(self):
        return f"{self.user.username} ({self.role})"


def get_or_create_profile(user) -> "UserProfile":
    """Return the user's profile, creating it on-the-fly if missing.

    The post_save signal normally creates one when a user is created, but
    users that pre-date the signal (or were created via bulk SQL) won't
    have one. Use this everywhere views touch ``user.userprofile`` so
    RelatedObjectDoesNotExist never reaches the user.
    """
    try:
        return user.userprofile
    except UserProfile.DoesNotExist:
        return UserProfile.objects.create(
            user=user,
            role="admin" if user.is_superuser else "student",
            allowed_modules=ALL_MODULES if user.is_superuser else [],
        )


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def ensure_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(
            user=instance,
            role="admin" if instance.is_superuser else "student",
            allowed_modules=ALL_MODULES if instance.is_superuser else [],
        )
    else:
        try:
            profile = instance.userprofile
        except UserProfile.DoesNotExist:
            UserProfile.objects.create(
                user=instance,
                role="admin" if instance.is_superuser else "student",
                allowed_modules=ALL_MODULES if instance.is_superuser else [],
            )
            return
        if instance.is_superuser and (
            profile.role != "admin" or set(profile.allowed_modules or []) != set(ALL_MODULES)
        ):
            profile.role = "admin"
            profile.allowed_modules = ALL_MODULES
            profile.save()
