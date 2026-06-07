"""URL configuration for OurProject."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from . import views_root


urlpatterns = [
    path("admin/", admin.site.urls),

    # Root — routes to dashboard if logged in, otherwise to login.
    path("", views_root.root_redirect, name="root"),

    # Whiteboard is no longer the landing page; it lives at /board/.
    path("board/", include("whiteboard.urls")),

    # New feature apps.
    path("explore/", include("apps.explorer.urls", namespace="explorer")),
    path("dashboard/", include("apps.dashboard.urls", namespace="dashboard")),
    path("tasks/", include("apps.tasks.urls", namespace="tasks")),
    path("reading/", include("apps.reading.urls", namespace="reading")),
    path("teacher/", include("apps.teacher.urls", namespace="teacher")),
    # Top-level "home" alias (sidebar, navbar) → the dashboard.
    path("home/", views_root.home, name="home"),
    # /modules/ — alias for the explorer hub.
    path("modules/", views_root.modules_root, name="modules"),
    # Accounts (login, signup, toggle-theme, …).
    path("accounts/", include("apps.accounts.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
