"""Dashboard view — gathers everything for the home page in one place.

Pulls modules, tasks, submissions, reading, and visits; assembles a
context the template can render without any further queries.
"""
from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone


@login_required
def home(request):
    from apps.accounts.models import get_or_create_profile
    from apps.explorer.mathlib import ALL_MODULES, MODULE_LABELS, MODULE_GROUPS

    profile = get_or_create_profile(request.user)
    user = request.user

    # ── 1. Modules — what is unlocked + which were visited ──────────────
    if profile.role == "admin" or user.is_superuser:
        allowed = list(ALL_MODULES)
    else:
        allowed = list(profile.allowed_modules or [])
    visited = set(profile.visited_modules or [])

    MODULES_META = [
        ("linear",     "Linear Functions",  "Algebra",   "y=mx+b",       "from-blue-500/20 to-blue-600/10",     "line-chart",  "lines & intercepts"),
        ("quadratic",  "Quadratics",        "Algebra",   "ax²+bx+c",     "from-violet-500/20 to-violet-600/10", "parentheses", "vertex & roots"),
        ("trig",       "Sine Waves",        "Algebra",   "A·sin(Bx+C)",  "from-cyan-500/20 to-cyan-600/10",     "waves",       "amp & period"),
        ("derivative", "Derivatives",       "Calculus",  "f′(x)",        "from-orange-500/20 to-orange-600/10", "trending-up", "secant → tangent"),
        ("integral",   "Integrals",         "Calculus",  "∫f(x)dx",      "from-green-500/20 to-green-600/10",   "sigma",       "Riemann sums"),
        ("geometry",   "Geometry",          "Geometry",  "△◻◯",          "from-pink-500/20 to-pink-600/10",     "shapes",      "11 shapes"),
        ("transform",  "Linear Transforms", "Geometry",  "[a b; c d]",   "from-amber-500/20 to-amber-600/10",   "move-3d",     "matrix M"),
    ]
    cards = []
    for slug, label, group, formula, gradient, icon, blurb in MODULES_META:
        if slug not in allowed:
            continue
        cards.append({
            "slug": slug, "label": label, "group": group,
            "formula": formula, "gradient": gradient, "icon": icon,
            "blurb": blurb,
            "visited": slug in visited,
        })

    # ── 2. Tasks — pending + done + reviewed counts ──────────────────────
    pending_tasks, recent_subs, reviewed_subs = [], [], []
    pending_count = done_count = reviewed_count = overdue_count = 0
    try:
        from apps.tasks.models import Task, Submission
        pending_tasks = list(
            Task.objects.exclude(submissions__student=user).order_by("due_date")[:5]
        )
        pending_count = Task.objects.exclude(submissions__student=user).count()
        all_user_subs = Submission.objects.filter(student=user)
        done_count = all_user_subs.count()
        reviewed_count = all_user_subs.filter(reviewed=True).count()
        recent_subs = list(all_user_subs.order_by("-submitted_at")[:5])
        reviewed_subs = list(all_user_subs.filter(reviewed=True).order_by("-submitted_at")[:3])
        # overdue = pending tasks whose due_date < today
        overdue_count = sum(1 for t in pending_tasks if t.is_overdue())
    except Exception:
        pass

    # ── 3. Reading recommendations ──────────────────────────────────────
    reading_recos = []
    try:
        from apps.reading.models import ReadingPage
        reading_recos = list(
            ReadingPage.objects.exclude(module_id="")
            .filter(module_id__in=allowed)
            .order_by("order", "title")[:4]
        )
        if not reading_recos:
            reading_recos = list(ReadingPage.objects.all()[:4])
    except Exception:
        pass

    # ── 4. Quick stats ──────────────────────────────────────────────────
    completion_pct = 0
    if pending_count + done_count > 0:
        completion_pct = int(round(100 * done_count / max(1, pending_count + done_count)))

    modules_unlocked = len(cards)
    modules_visited = sum(1 for c in cards if c["visited"])

    stats = [
        {
            "label": "Modules unlocked",
            "value": f"{modules_unlocked}",
            "sub": f"{modules_visited} visited",
            "accent": "blue",
            "icon": "M3 3v18h18",
        },
        {
            "label": "Tasks completed",
            "value": f"{done_count}",
            "sub": f"{pending_count} pending · {overdue_count} overdue",
            "accent": "violet",
            "icon": "M9 12l2 2 4-4M21 12a9 9 0 11-18 0 9 9 0 0118 0z",
        },
        {
            "label": "Reviewed",
            "value": f"{reviewed_count}",
            "sub": f"{done_count - reviewed_count} awaiting feedback",
            "accent": "emerald",
            "icon": "M5 13l4 4L19 7",
        },
        {
            "label": "Streak",
            "value": f"{min(7, modules_visited + 1)}d",
            "sub": "Keep it going!",
            "accent": "amber",
            "icon": "M12 2s4 4 4 8a4 4 0 11-8 0c0-4 4-8 4-8z",
        },
    ]

    # ── 5. Quick actions ────────────────────────────────────────────────
    quick_actions = [
        {"label": "Read a lesson",     "href": "accounts:lessons",   "icon": "book",   "accent": "blue"},
        {"label": "Open tasks",         "href": "tasks:list",        "icon": "list",   "accent": "violet"},
        {"label": "Browse modules",     "href": "explorer:index",    "icon": "grid",   "accent": "emerald"},
        {"label": "Get help",           "href": "accounts:help",     "icon": "help",   "accent": "amber"},
    ]

    return render(request, "dashboard/home.html", {
        "cards": cards,
        "pending_tasks": pending_tasks,
        "recent_subs": recent_subs,
        "reviewed_subs": reviewed_subs,
        "reading_recos": reading_recos,
        "stats": stats,
        "quick_actions": quick_actions,
        "completion_pct": completion_pct,
        "modules_unlocked": modules_unlocked,
        "modules_visited": modules_visited,
        "profile": profile,
    })
