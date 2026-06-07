"""mathlib package — pure-Python math, no Django imports allowed."""

from . import linear, quadratic, trig, derivative, integral, geometry, transform, statistics
from .plotly_bridge import build_plot


ALL_MODULES = ["linear", "quadratic", "trig", "derivative", "integral", "geometry", "transform", "statistics"]
MODULE_LABELS = {
    "linear": "Linear Functions",
    "quadratic": "Quadratics",
    "trig": "Sine Waves",
    "derivative": "Derivatives",
    "integral": "Integrals",
    "geometry": "Geometry",
    "transform": "Linear Transforms",
    "statistics": "Statistics",
}
MODULE_GROUPS = {
    "linear": "Algebra", "quadratic": "Algebra", "trig": "Algebra",
    "derivative": "Calculus", "integral": "Calculus",
    "geometry": "Geometry", "transform": "Geometry",
    "statistics": "Statistics",
}

MODULES = {
    "linear": linear,
    "quadratic": quadratic,
    "trig": trig,
    "derivative": derivative,
    "integral": integral,
    "geometry": geometry,
    "transform": transform,
    "statistics": statistics,
}


def get_module(slug: str):
    return MODULES[slug]
