"""Form definitions for each explorer module.

Slider ranges match the React version 1:1 (see DECISIONS.md).
"""

from django import forms


class LinearForm(forms.Form):
    m = forms.FloatField(
        min_value=-1000, max_value=1000, initial=1.0,
        widget=forms.NumberInput(attrs={"step": "0.1"}),
    )
    b = forms.FloatField(
        min_value=-1000, max_value=1000, initial=0.0,
        widget=forms.NumberInput(attrs={"step": "0.1"}),
    )


class QuadraticForm(forms.Form):
    a = forms.FloatField(min_value=-1000, max_value=1000, initial=1.0,
                         widget=forms.NumberInput(attrs={"step": "0.1"}))
    b = forms.FloatField(min_value=-1000, max_value=1000, initial=0.0,
                         widget=forms.NumberInput(attrs={"step": "0.1"}))
    c = forms.FloatField(min_value=-1000, max_value=1000, initial=0.0,
                         widget=forms.NumberInput(attrs={"step": "0.1"}))


class TrigForm(forms.Form):
    A = forms.FloatField(min_value=-1000, max_value=1000, initial=1.0,
                         widget=forms.NumberInput(attrs={"step": "0.1"}))
    B = forms.FloatField(min_value=-1000, max_value=1000, initial=1.0,
                         widget=forms.NumberInput(attrs={"step": "0.05"}))
    C = forms.FloatField(min_value=-3141.59, max_value=3141.59, initial=0.0,
                         widget=forms.NumberInput(attrs={"step": "0.1"}))
    D = forms.FloatField(min_value=-1000, max_value=1000, initial=0.0,
                         widget=forms.NumberInput(attrs={"step": "0.1"}))


class DerivativeForm(forms.Form):
    FN_CHOICES = [("poly", "f(x)=x²"), ("cubic", "f(x)=x³−3x"),
                  ("sin", "f(x)=sin(x)"), ("exp", "f(x)=e^(x/3)"),
                  ("abs", "f(x)=|x|")]
    fn_key = forms.ChoiceField(choices=FN_CHOICES, initial="poly")
    x0 = forms.FloatField(min_value=-1000, max_value=1000, initial=1.0,
                          widget=forms.NumberInput(attrs={"step": "0.05"}))
    h = forms.FloatField(min_value=0.001, max_value=1000, initial=0.5,
                         widget=forms.NumberInput(attrs={"step": "0.01"}))


class IntegralForm(forms.Form):
    FN_CHOICES = [("poly", "f(x)=x²/4"), ("quad", "f(x)=−x²+9"),
                  ("sin",  "f(x)=2·sin(x)+3"), ("exp",  "f(x)=e^(x/3)")]
    METHOD_CHOICES = [("left", "Left"), ("right", "Right"),
                      ("midpoint", "Midpoint"), ("trapezoid", "Trapezoid")]
    fn_key = forms.ChoiceField(choices=FN_CHOICES, initial="poly")
    a = forms.FloatField(min_value=-1000, max_value=1000, initial=0.0,
                         widget=forms.NumberInput(attrs={"step": "0.1"}))
    b = forms.FloatField(min_value=-1000, max_value=1000, initial=4.0,
                         widget=forms.NumberInput(attrs={"step": "0.1"}))
    n = forms.IntegerField(min_value=1, max_value=10000, initial=20)
    method = forms.ChoiceField(choices=METHOD_CHOICES, initial="midpoint")

    def clean(self):
        cleaned = super().clean()
        a = cleaned.get("a")
        b = cleaned.get("b")
        if a is not None and b is not None and a >= b:
            raise forms.ValidationError("b must be strictly greater than a.")
        return cleaned


class GeometryForm(forms.Form):
    SHAPES = ["circle", "ellipse", "square", "rectangle", "triangle",
              "rightTriangle", "parallelogram", "trapezoid", "rhombus",
              "sector", "polygon"]
    shape = forms.ChoiceField(choices=[(s, s) for s in SHAPES], initial="circle")
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
    n          = forms.IntegerField(min_value=3,  max_value=20, initial=6)
    r_polygon  = forms.FloatField(min_value=0.1, max_value=15, initial=5.0, required=False)
    rotation_deg = forms.FloatField(min_value=0, max_value=359, initial=0.0, required=False)

    def clean(self):
        cleaned = super().clean()
        shape = cleaned.get("shape") or "circle"
        from .mathlib.geometry import SHAPE_DEFAULTS
        for k, v in SHAPE_DEFAULTS[shape].items():
            if k not in cleaned or cleaned.get(k) is None:
                cleaned[k] = v
        return cleaned


class TransformForm(forms.Form):
    a = forms.FloatField(min_value=-1000, max_value=1000, initial=1.0,
                         widget=forms.NumberInput(attrs={"step": "0.05"}))
    b = forms.FloatField(min_value=-1000, max_value=1000, initial=0.0,
                         widget=forms.NumberInput(attrs={"step": "0.05"}))
    c = forms.FloatField(min_value=-1000, max_value=1000, initial=0.0,
                         widget=forms.NumberInput(attrs={"step": "0.05"}))
    d = forms.FloatField(min_value=-1000, max_value=1000, initial=1.0,
                         widget=forms.NumberInput(attrs={"step": "0.05"}))


FORM_MAP = {
    "linear":     (LinearForm,     ["m", "b"]),
    "quadratic":  (QuadraticForm,  ["a", "b", "c"]),
    "trig":       (TrigForm,       ["A", "B", "C", "D"]),
    "derivative": (DerivativeForm, ["fn_key", "x0", "h"]),
    "integral":   (IntegralForm,   ["fn_key", "a", "b", "n", "method"]),
    "geometry":   (GeometryForm,   ["shape"]),
    "transform":  (TransformForm,  ["a", "b", "c", "d"]),
}
