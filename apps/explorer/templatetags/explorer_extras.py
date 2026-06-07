from django import template

register = template.Library()


@register.filter
def get_item(obj, key):
    """dict[key] or list[int] — returns '' on KeyError/IndexError."""
    try:
        if isinstance(obj, dict):
            return obj.get(key, "")
        return obj[int(key)]
    except (KeyError, IndexError, TypeError, ValueError):
        return ""


@register.filter
def module_title(slug):
    """'linear' → 'Linear', 'trig' → 'Trigonometry'."""
    labels = {
        "linear":     "Linear Functions",
        "quadratic":  "Quadratics",
        "trig":       "Trigonometry",
        "derivative": "Derivatives",
        "integral":   "Integrals",
        "geometry":   "Geometry",
        "transform":  "Linear Transforms",
        "statistics": "Statistics",
    }
    return labels.get(slug, str(slug).capitalize())
