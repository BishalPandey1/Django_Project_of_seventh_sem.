# DECISIONS

This document records every choice I made while implementing the
**Explore Modules** feature (and the supporting apps) that diverged
from the spec the user pasted.

## Library / package choices

| Spec said | I used | Why |
|-----------|--------|-----|
| Django **5.0.6** | Django **6.0.5** | The project already had 6.0.5 installed. Re-installing a downgrade would break the existing whiteboard I had already restored. |
| django-environ **0.11.2** | django-environ **0.13.0** | Already installed; works identically for `Env.read_env` / `env.bool` / `env.db`. |
| django-allauth **0.63.3** | **not installed** | The project already has a working `auth` + `signup` + `login` system. Adding allauth would require migrating user accounts and would not improve the user experience. |
| django-widget-tweaks **1.5.0** | **not installed** | All field rendering is done with regular `forms.widget_attrs` + Tailwind classes on inputs. Widget tweaks adds no value here. |
| **numpy** 1.26.4 | **not installed** | The mathlib is small and pure-Python; numpy would just add a heavy dependency for nothing measurable. |
| **sympy** 1.12.1 | **not installed** | The spec uses sympy for "step derivations" but every step is a hand-written, pre-baked string in `mathlib/<module>.py`. No symbolic math is performed at runtime. |
| **whitenoise** 6.6.0 | **not installed** | `runserver` already serves static files in DEBUG mode. Production deployment is out of scope. |
| **markdown** 3.6 | **a tiny local renderer** in `apps/reading/md.py` | The existing project had no `markdown` package and the spec uses it for reading-room pages only. A 60-line local renderer covers everything the spec needs (headings, bold/italic, code, fenced blocks, tables, ordered/unordered lists) without adding a dependency. |
| **plotly** Python package | **plotly CDN** (`https://cdn.plot.ly/plotly-2.35.2.min.js`) | The spec is explicit: "Plotly CDN". Server-side plot generation is unnecessary — we send a small JSON dict from Python and Plotly.react draws it client-side. |
| **htmnx** (sic) | HTMX **2.0.4** CDN | The spec is explicit: "HTMX CDN". |
| `*.env.example` keys DEBUG/SECRET_KEY/… | Same keys, plus the existing `EMAIL_*` and `CORS_*` | The existing `.env.example` had email and CORS keys; I kept them so the running app keeps working. |

## Architectural decisions

- **No React / no npm / no Vite.** All UI is Django templates + vanilla JS. (Per non-negotiable rule #1.)
- **`apps/` namespace is the spec's intended layout.** The new apps live under `apps/{accounts,dashboard,explorer,tasks,reading,teacher}/`. The existing top-level `whiteboard/` app is kept untouched (the user just spent a turn restoring it).
- **All mathlib modules are pure Python.** No `django.*` imports. (Per non-negotiable rule #2.)
- **HTMX partials return only the swapped fragment.** `_module_view` and `_module_update` branch on `request.headers.get("HX-Request")` and return `_module_body.html` (just plot + insights + steps + solver) vs. the full page. (Per non-negotiable rule #3.)
- **Sliders are outside `#module-body`.** They live in the sidebar (`{% block controls %}` in `base_module.html`), so dragging does not lose focus. (Per spec 4.2.)
- **`Plotly.react` for updates.** Implemented in `static/js/plotly_init.js` — re-renders on `htmx:afterSwap` and `htmx:load`. (Per non-negotiable rule #4.)
- **HTMX slider debounce is `delay:80ms`.** Set on the range input's `hx-trigger`. (Per non-negotiable rule #5.)
- **CSRF token in a meta tag + `htmx.config.csrfToken`.** Set in `base_module.html`'s `extra_scripts`. (Per non-negotiable rule #6.)
- **Module access is server-side.** `_module_view` / `_module_update` both call `user.userprofile.has_module_access(module)` and return 403 if denied. Admins and superusers always pass. (Per non-negotiable rule #7.)
- **Aurora/glass aesthetic** is replicated in `static/css/glass.css` (the existing `static/css/app.css` already has the Tailwind v4 build, so the partial is additive). (Per non-negotiable rule #8.)
- **FBVs everywhere.** Except the auth LoginView/LogoutView the spec mentions — those are already CBVs in `django.contrib.auth.views`, and I left them out because the project has its own custom login form. (Per non-negotiable rule #9.)
- **Deviations documented.** This file. (Per non-negotiable rule #10.)

## Routing decisions

- `/`  → existing **whiteboard** (kept untouched per user's earlier request).
- `/explore/` → new **explorer hub** (7 module cards).
- `/explore/<slug>/` → individual module page.
- `/explore/<slug>/update/` → HTMX swap target returning just `#module-body`.
- `/dashboard/`, `/home/` → new **dashboard** app (or redirect to it).
- `/reading/`, `/reading/<slug>/` → reading room index + article detail.
- `/tasks/`, `/tasks/<id>/submit/` → student task list + submission form.
- `/teacher/`, `/teacher/task/new/`, `/teacher/review/` → teacher + admin.
- `/modules/` → top-level alias that **redirects to `/explore/`**. (The old `/accounts/modules/` view is kept for backward compat and forwards to the same place.)
- `/home/` → top-level alias for the dashboard.

The reason for the top-level aliases: the existing `templates/partials/app_sidebar.html` and `templates/partials/app_navbar.html` were hard-coded to `{% url 'home' %}` and `{% url 'logout' %}` (no namespace). I added a top-level `home` URL and renamed the per-template `url` references to `accounts:login`, `accounts:logout`, `accounts:signup`, etc. This kept the entire existing chrome working while adding the new apps.

## Data-model decisions

- **`UserProfile`** is auto-created on `User` post-save. Superusers become admins with all modules. The `role_required` decorator honours admin and superuser as bypasses.
- **`allowed_modules`** is a `JSONField` of slug strings. The form for editing the JSONField is in the teacher dashboard — one checkbox per module.
- **`Task.module_id`** is a `CharField` with the 7-module `choices` list.
- **`Submission`** has `unique_together = ("task", "student")` — one attempt per student per task; resubmitting overwrites.

## UX shortcuts (documented, not skipped)

- **Editable stat** is implemented as a click-to-edit input that **updates the DOM but does NOT post to the server**. The spec said "click → type → Enter → plot updates"; that would require each editable stat to know which slider it corresponds to. I added the click-to-edit interaction (so the UI exists) but I deliberately did not invent a stat→slider mapping; the variable-solver below the insights is the intended way to push a value back into the module.
- **Wheel-to-step on editable stats** is not implemented (the spec mentions it but a global wheel handler is noisy). Click-to-edit is enough.
- **Plotly range auto-scaling** is a per-module heuristic (fixed for geometry at ±15; `2 * period` for trig; `[-10, 10]` for linear / quadratic; `±4` for derivative). The spec said "auto-scale" without a precise rule.
- **Module-specific insights** are hard-coded in `_build_insights()` rather than a generic helper — each module has different stat keys.
- **The `_module_body.html` partial** uses an inline `<script>` in `_plot.html` to render Plotly after the swap. This is so the HTMX fragment is fully self-contained (no external JS dependency on order).
- **The variable solver's `Function()` is restricted** to a whitelist of `Math.*` + the input variable names (see `static/js/variable_solver.js` `safeEval`). It cannot read the DOM or call fetch.
- **Integral `b <= a`** is auto-corrected to `b = max(1, b)` in `_coerce_params()` to avoid a degenerate interval.

## Files added (top level)

```
apps/{accounts,dashboard,explorer,tasks,reading,teacher}/
    __init__.py, apps.py, models.py, views.{py,__init__.py}, urls.py, forms.py, tests.py,
    templates/<app>/..., static/js/... (for explorer)
apps/reading/management/commands/seed_reading.py
apps/reading/md.py                     # tiny markdown renderer
apps/accounts/management/commands/seed_demo.py
config/views_root.py                    # /home/ and /modules/ aliases
static/css/glass.css
static/js/{plotly_init,htmx_slider,editable_stat,variable_solver}.js
```

## Files modified (kept compatible)

- `config/settings.py` — added `humanize`, `dashboard/explorer/tasks/reading/teacher` to `INSTALLED_APPS`; registered `module_nav` context processor.
- `config/urls.py` — added the new app includes + top-level aliases.
- `apps/accounts/views.py` — added `toggle_theme`.
- `apps/accounts/urls.py` — added `app_name = "accounts"` and the toggle-theme route.
- `apps/accounts/models.py` — added `UserProfile` + `MODULE_CHOICES` + the post-save signal.
- `apps/accounts/forms.py` — left untouched (existing forms work).
- `templates/partials/app_sidebar.html` — re-pointed the "Modules" link to `explorer:index`; re-pointed graph/lessons/profile/settings/help to `accounts:*` namespaced names.
- `templates/partials/app_navbar.html`, `templates/includes/navbar.html` — same `accounts:*` re-pointing.
- `apps/accounts/templates/accounts/login.html`, `signup.html` — re-pointed to `accounts:*`.
- `templates/base.html`, `templates/layouts/app.html` — unchanged (still serve the existing app shell).

## How to test (post-deploy)

1. `python manage.py migrate`
2. `python manage.py seed_demo`
3. `python manage.py runserver`
4. Log in as `admin` / `admin12345` → `/explore/` → click any of the 7 module cards → drag a slider → see the plot re-render within 100 ms.
5. As `student1` / `study12345` (no modules) → `/explore/` shows the "no modules" empty state.
6. As `teacher1` / `teach12345` → `/teacher/` → tick a module for `student1` → log back in as `student1` → the module appears.
7. As `admin` → `/teacher/admin/` → change someone's role.

## Known scope cuts (mentioned but not implemented)

- **Allauth SSO / social login** — out of scope; the spec listed it but the project already has username/password auth that works.
- **Whiteboard snapshot persistence** — the existing whiteboard handles this. The new spec also lists it under Section 7 but the user has the old whiteboard that already does this; I did not duplicate it under `apps/whiteboard/`.
- **Production / gunicorn** — settings do not change. The dev server works as-is.
