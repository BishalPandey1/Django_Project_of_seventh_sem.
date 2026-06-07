"""Form definitions for each explorer module.

All fields are ``required=False`` so that a single-slider HTMX POST is a
valid form (we only need the fields the user actually moved). The
``clean()`` method on each form fills in the field ``initial`` for any
key the user did not submit, so the mathlib always gets a complete
parameter set.
"""

from django import forms


def _fill_defaults(form, default_keys=None):
    """Populate ``cleaned_data`` with the field ``initial`` for any missing
    key. If ``default_keys`` is given, only those keys are touched (use
    this for GeometryForm so the per-shape defaults stay authoritative).

    ChoiceField with ``required=False`` returns ``''`` (not ``None``)
    when missing, so we treat both as "missing".
    """
    cleaned = form.cleaned_data
    for name, field in form.fields.items():
        if default_keys and name not in default_keys:
            continue
        value = cleaned.get(name)
        if value in (None, "") and field.initial not in (None, ""):
            cleaned[name] = field.initial
    return cleaned


class LinearForm(forms.Form):
    m = forms.FloatField(
        min_value=-1000, max_value=1000, initial=1.0, required=False,
        widget=forms.NumberInput(attrs={"step": "0.1"}),
    )
    b = forms.FloatField(
        min_value=-1000, max_value=1000, initial=0.0, required=False,
        widget=forms.NumberInput(attrs={"step": "0.1"}),
    )

    def clean(self):
        return _fill_defaults(self)


class QuadraticForm(forms.Form):
    a = forms.FloatField(min_value=-1000, max_value=1000, initial=1.0, required=False,
                         widget=forms.NumberInput(attrs={"step": "0.1"}))
    b = forms.FloatField(min_value=-1000, max_value=1000, initial=0.0, required=False,
                         widget=forms.NumberInput(attrs={"step": "0.1"}))
    c = forms.FloatField(min_value=-1000, max_value=1000, initial=0.0, required=False,
                         widget=forms.NumberInput(attrs={"step": "0.1"}))

    def clean(self):
        return _fill_defaults(self)


class TrigForm(forms.Form):
    A = forms.FloatField(min_value=-1000, max_value=1000, initial=1.0, required=False,
                         widget=forms.NumberInput(attrs={"step": "0.1"}))
    B = forms.FloatField(min_value=-1000, max_value=1000, initial=1.0, required=False,
                         widget=forms.NumberInput(attrs={"step": "0.05"}))
    C = forms.FloatField(min_value=-3141.59, max_value=3141.59, initial=0.0, required=False,
                         widget=forms.NumberInput(attrs={"step": "0.1"}))
    D = forms.FloatField(min_value=-1000, max_value=1000, initial=0.0, required=False,
                         widget=forms.NumberInput(attrs={"step": "0.1"}))

    def clean(self):
        return _fill_defaults(self)


class DerivativeForm(forms.Form):
    FN_CHOICES = [("poly", "f(x)=x²"), ("cubic", "f(x)=x³−3x"),
                  ("sin", "f(x)=sin(x)"), ("exp", "f(x)=e^(x/3)"),
                  ("abs", "f(x)=|x|")]
    fn_key = forms.ChoiceField(choices=FN_CHOICES, initial="poly", required=False)
    x0 = forms.FloatField(min_value=-1000, max_value=1000, initial=1.0, required=False,
                          widget=forms.NumberInput(attrs={"step": "0.05"}))
    h = forms.FloatField(min_value=0.001, max_value=1000, initial=0.5, required=False,
                         widget=forms.NumberInput(attrs={"step": "0.01"}))

    def clean(self):
        return _fill_defaults(self)


class IntegralForm(forms.Form):
    FN_CHOICES = [("poly", "f(x)=x²/4"), ("quad", "f(x)=−x²+9"),
                  ("sin",  "f(x)=2·sin(x)+3"), ("exp",  "f(x)=e^(x/3)")]
    METHOD_CHOICES = [("left", "Left"), ("right", "Right"),
                      ("midpoint", "Midpoint"), ("trapezoid", "Trapezoid")]
    fn_key = forms.ChoiceField(choices=FN_CHOICES, initial="poly", required=False)
    a = forms.FloatField(min_value=-1000, max_value=1000, initial=0.0, required=False,
                         widget=forms.NumberInput(attrs={"step": "0.1"}))
    b = forms.FloatField(min_value=-1000, max_value=1000, initial=4.0, required=False,
                         widget=forms.NumberInput(attrs={"step": "0.1"}))
    n = forms.IntegerField(min_value=1, max_value=10000, initial=20, required=False)
    method = forms.ChoiceField(choices=METHOD_CHOICES, initial="midpoint", required=False)

    def clean(self):
        cleaned = _fill_defaults(self)
        a = cleaned.get("a")
        b = cleaned.get("b")
        if a is not None and b is not None and a >= b:
            # Swap so the mathlib never gets an empty interval.
            cleaned["a"], cleaned["b"] = b, a
        return cleaned


class GeometryForm(forms.Form):
    SHAPES = ["circle", "ellipse", "square", "rectangle", "triangle",
              "rightTriangle", "parallelogram", "trapezoid", "rhombus",
              "sector", "polygon"]
    shape = forms.ChoiceField(choices=[(s, s) for s in SHAPES], initial="circle", required=False)
    r  = forms.FloatField(min_value=0.1, max_value=15, initial=3.0, required=False)
    cx = forms.FloatField(min_value=-15, max_value=15, initial=0.0, required=False)
    cy = forms.FloatField(min_value=-15, max_value=15, initial=0.0, required=False)
    rx = forms.FloatField(min_value=0.1, max_value=15, initial=5.0, required=False)
    ry = forms.FloatField(min_value=0.1, max_value=15, initial=3.0, required=False)
    s  = forms.FloatField(min_value=0.1, max_value=15, initial=4.0, required=False)
    L  = forms.FloatField(min_value=0.1, max_value=15, initial=6.0, required=False)
    W  = forms.FloatField(min_value=0.1, max_value=15, initial=4.0, required=False)
    Ax = forms.FloatField(min_value=-15, max_value=15, initial=-3.0, required=False)
    Ay = forms.FloatField(min_value=-15, max_value=15, initial=-2.0, required=False)
    Bx = forms.FloatField(min_value=-15, max_value=15, initial=3.0, required=False)
    By = forms.FloatField(min_value=-15, max_value=15, initial=-2.0, required=False)
    Cx = forms.FloatField(min_value=-15, max_value=15, initial=0.0, required=False)
    Cy = forms.FloatField(min_value=-15, max_value=15, initial=3.0, required=False)
    a  = forms.FloatField(min_value=0.1, max_value=15, initial=4.0, required=False)
    b  = forms.FloatField(min_value=0.1, max_value=15, initial=3.0, required=False)
    base       = forms.FloatField(min_value=0.1, max_value=15, initial=5.0, required=False)
    side       = forms.FloatField(min_value=0.1, max_value=15, initial=3.0, required=False)
    angle_deg  = forms.FloatField(min_value=1,    max_value=170, initial=60.0, required=False)
    h          = forms.FloatField(min_value=0.1, max_value=15, initial=4.0, required=False)
    p          = forms.FloatField(min_value=0.1, max_value=15, initial=6.0, required=False)
    q          = forms.FloatField(min_value=0.1, max_value=15, initial=4.0, required=False)
    theta_deg  = forms.FloatField(min_value=1,    max_value=359, initial=60.0, required=False)
    n          = forms.IntegerField(min_value=3,  max_value=20, initial=6, required=False)
    r_polygon  = forms.FloatField(min_value=0.1, max_value=15, initial=5.0, required=False)
    rotation_deg = forms.FloatField(min_value=0, max_value=359, initial=0.0, required=False)

    def clean(self):
        cleaned = _fill_defaults(self)
        shape = cleaned.get("shape") or "circle"
        from .mathlib.geometry import SHAPE_DEFAULTS
        # SHAPE_DEFAULTS for the current shape is the source of truth.
        # User-submitted values (anything in self.data) win; for keys the
        # user did NOT touch, SHAPE_DEFAULTS supplies a coherent value
        # (overriding the per-field initial that may belong to another
        # shape entirely).
        submitted = set(self.data.keys())
        for k, v in SHAPE_DEFAULTS.get(shape, {}).items():
            if k not in submitted:
                cleaned[k] = v
        return cleaned


class TransformForm(forms.Form):
    a = forms.FloatField(min_value=-1000, max_value=1000, initial=1.0, required=False,
                         widget=forms.NumberInput(attrs={"step": "0.05"}))
    b = forms.FloatField(min_value=-1000, max_value=1000, initial=0.0, required=False,
                         widget=forms.NumberInput(attrs={"step": "0.05"}))
    c = forms.FloatField(min_value=-1000, max_value=1000, initial=0.0, required=False,
                         widget=forms.NumberInput(attrs={"step": "0.05"}))
    d = forms.FloatField(min_value=-1000, max_value=1000, initial=1.0, required=False,
                         widget=forms.NumberInput(attrs={"step": "0.05"}))

    def clean(self):
        return _fill_defaults(self)


class StatisticsForm(forms.Form):
    mean   = forms.FloatField(min_value=-5,  max_value=5,   initial=0.0, required=False,
                              widget=forms.NumberInput(attrs={"step": "0.1"}))
    stddev = forms.FloatField(min_value=0.5, max_value=3,   initial=1.0, required=False,
                              widget=forms.NumberInput(attrs={"step": "0.1"}))
    n      = forms.IntegerField(min_value=10, max_value=200, initial=50,  required=False,
                                widget=forms.NumberInput(attrs={"step": "1"}))
    bins   = forms.IntegerField(min_value=5,  max_value=25,  initial=10,  required=False,
                                widget=forms.NumberInput(attrs={"step": "1"}))

    def clean(self):
        return _fill_defaults(self)


FORM_MAP = {
    "linear":     (LinearForm,     ["m", "b"]),
    "quadratic":  (QuadraticForm,  ["a", "b", "c"]),
    "trig":       (TrigForm,       ["A", "B", "C", "D"]),
    "derivative": (DerivativeForm, ["fn_key", "x0", "h"]),
    "integral":   (IntegralForm,   ["fn_key", "a", "b", "n", "method"]),
    "geometry":   (GeometryForm,   ["shape"]),
    "transform":  (TransformForm,  ["a", "b", "c", "d"]),
    "statistics": (StatisticsForm, ["mean", "stddev", "n", "bins"]),
}
