"""Top-level explorer views — one pair per module (GET + HTMX update)."""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from ._module_common import _module_view, _module_update, _module_snapshot


def _wrapped(module, template):
    @login_required
    def view(request):
        return _module_view(request, module, template)
    return view


def _wrapped_update(module):
    @login_required
    def view(request):
        return _module_update(request, module)
    return view


def _wrapped_snapshot(module):
    @login_required
    def view(request):
        return _module_snapshot(request, module)
    return view


linear_view     = _wrapped("linear",     "linear")
quadratic_view  = _wrapped("quadratic",  "quadratic")
trig_view       = _wrapped("trig",       "trig")
derivative_view = _wrapped("derivative", "derivative")
integral_view   = _wrapped("integral",   "integral")
geometry_view   = _wrapped("geometry",   "geometry")
transform_view  = _wrapped("transform",  "transform")

linear_update     = _wrapped_update("linear")
quadratic_update  = _wrapped_update("quadratic")
trig_update       = _wrapped_update("trig")
derivative_update = _wrapped_update("derivative")
integral_update   = _wrapped_update("integral")
geometry_update   = _wrapped_update("geometry")
transform_update  = _wrapped_update("transform")

linear_snapshot     = _wrapped_snapshot("linear")
quadratic_snapshot  = _wrapped_snapshot("quadratic")
trig_snapshot       = _wrapped_snapshot("trig")
derivative_snapshot = _wrapped_snapshot("derivative")
integral_snapshot   = _wrapped_snapshot("integral")
geometry_snapshot   = _wrapped_snapshot("geometry")
transform_snapshot  = _wrapped_snapshot("transform")


@login_required
def modules_index(request):
    """Hub page — list of all 7 modules with access info."""
    from apps.explorer.mathlib import ALL_MODULES, MODULE_LABELS, MODULE_GROUPS
    from apps.accounts.models import get_or_create_profile
    profile = get_or_create_profile(request.user)
    cards = []
    metas = [
        ("linear",     "y = m·x + b",           "from-blue-500/20 to-blue-600/10",     "line-chart"),
        ("quadratic",  "a·x² + b·x + c",        "from-violet-500/20 to-violet-600/10", "parentheses"),
        ("trig",       "A·sin(B·x + C) + D",    "from-cyan-500/20 to-cyan-600/10",     "waves"),
        ("derivative", "f′(x) tangent/secant",  "from-orange-500/20 to-orange-600/10", "trending-up"),
        ("integral",   "Riemann sum",           "from-green-500/20 to-green-600/10",   "sigma"),
        ("geometry",   "11 shapes",             "from-pink-500/20 to-pink-600/10",     "shapes"),
        ("transform",  "[a b; c d]·v",          "from-amber-500/20 to-amber-600/10",   "move-3d"),
    ]
    for slug, formula, gradient, icon in metas:
        if profile.has_module_access(slug):
            cards.append({
                "slug": slug,
                "label": MODULE_LABELS[slug],
                "group": MODULE_GROUPS[slug],
                "formula": formula,
                "gradient": gradient,
                "icon": icon,
            })
    return render(request, "explorer/index.html", {"cards": cards})
