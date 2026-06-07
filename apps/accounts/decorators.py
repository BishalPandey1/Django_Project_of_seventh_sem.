"""Role-based view decorator."""

from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def role_required(*roles):
    """Allow only users whose profile role is in ``roles`` (or superuser)."""

    def deco(view):
        @wraps(view)
        @login_required
        def wrapped(request, *args, **kwargs):
            profile = getattr(request.user, "userprofile", None)
            if request.user.is_superuser:
                return view(request, *args, **kwargs)
            if profile is None or profile.role not in roles:
                raise PermissionDenied
            return view(request, *args, **kwargs)

        return wrapped

    return deco
