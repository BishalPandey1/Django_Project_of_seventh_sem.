"""URL helpers living at the project root."""

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


def root_redirect(request):
    """Root of the site.

    - Logged-in users go straight to the dashboard.
    - Everyone else is sent to the login page.
    """
    if request.user.is_authenticated:
        return redirect("dashboard:home")
    return redirect("accounts:login")


@login_required
def home(request):
    """Top-level /home/ alias — redirects to the dashboard."""
    return redirect("dashboard:home")


@login_required
def modules_root(request):
    """Top-level /modules/ alias — redirects to the explorer hub."""
    return redirect("explorer:index")
