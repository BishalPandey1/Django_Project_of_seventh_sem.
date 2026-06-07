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

    # ── 1b. Featured "continue" card — the most recently visited module
    # (if any) becomes the hero recommendation.
    visited_order = list(profile.visited_modules or [])
    continue_card = None
    for slug in reversed(visited_order):
        match = next((c for c in cards if c["slug"] == slug), None)
        if match:
            continue_card = match
            break
    if not continue_card and cards:
        continue_card = cards[0]

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
    reading_featured = None
    try:
        from apps.reading.models import ReadingPage
        reading_recos = list(
            ReadingPage.objects.exclude(module_id="")
            .filter(module_id__in=allowed)
            .order_by("order", "title")[:4]
        )
        if not reading_recos:
            reading_recos = list(ReadingPage.objects.all()[:4])
        # Feature the reading for the last visited module (if any), else the
        # first chapter — gives a "real book" feel on the dashboard.
        if reading_recos:
            for r in reading_recos:
                if r.module_id in visited:
                    reading_featured = r
                    break
            if not reading_featured:
                reading_featured = reading_recos[0]
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
        {
            "label": "Read a lesson",
            "description": "Step-by-step theory with examples",
            "href": "accounts:lessons",
            "icon": "M4 19.5A2.5 2.5 0 0 1 6.5 17H20M4 19.5A2.5 2.5 0 0 1 6.5 22H20V2H6.5A2.5 2.5 0 0 0 4 4.5v15z",
            "accent": "blue",
        },
        {
            "label": "Open tasks",
            "description": "Practice problems to solve",
            "href": "tasks:list",
            "icon": "M9 11l3 3L22 4M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11",
            "accent": "violet",
        },
        {
            "label": "Browse modules",
            "description": "Explore all interactive topics",
            "href": "explorer:index",
            "icon": "M3 3h7v7H3zM14 3h7v7h-7zM14 14h7v7h-7zM3 14h7v7H3z",
            "accent": "emerald",
        },
        {
            "label": "Whiteboard",
            "description": "Sketch, draw & annotate",
            "href": "whiteboard:whiteboard-page",
            "icon": "M12 19l7-7 3 3-7 7-3-3zM18 13l-1.5-7.5L2 2l3.5 14.5L13 18l5-5zM2 2l7.586 7.586",
            "accent": "amber",
        },
    ]

    return render(request, "dashboard/home.html", {
        "cards": cards,
        "continue_card": continue_card,
        "pending_tasks": pending_tasks,
        "recent_subs": recent_subs,
        "reviewed_subs": reviewed_subs,
        "reading_recos": reading_recos,
        "reading_featured": reading_featured,
        "stats": stats,
        "quick_actions": quick_actions,
        "completion_pct": completion_pct,
        "modules_unlocked": modules_unlocked,
        "modules_visited": modules_visited,
        "profile": profile,
    })
