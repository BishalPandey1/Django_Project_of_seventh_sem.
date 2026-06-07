"""Context processor — exposes module navigation to every template."""

from apps.explorer.mathlib import ALL_MODULES, MODULE_LABELS


def module_nav(request):
    return {
        "module_nav": [(slug, MODULE_LABELS[slug]) for slug in ALL_MODULES],
    }
