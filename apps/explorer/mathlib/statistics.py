"""Pure-Python math for the statistics / normal-distribution module. No Django imports."""

import math


PRESETS = [
    {"name": "Standard Normal",  "params": {"mean": 0, "stddev": 1, "n": 50,  "bins": 10},
     "blurb": "μ = 0, σ = 1 — the classic bell curve."},
    {"name": "Wide Spread",      "params": {"mean": 0, "stddev": 2, "n": 100, "bins": 15},
     "blurb": "μ = 0, σ = 2 — flatter and wider."},
    {"name": "Right Shift",      "params": {"mean": 3, "stddev": 0.8, "n": 50,  "bins": 10},
     "blurb": "μ = 3, σ = 0.8 — shifted right, tighter."},
    {"name": "Large Sample",     "params": {"mean": 0, "stddev": 1, "n": 200, "bins": 20},
     "blurb": "n = 200 — smoother histogram."},
    {"name": "Narrow & Tall",    "params": {"mean": 1, "stddev": 0.5, "n": 30,  "bins": 8},
     "blurb": "μ = 1, σ = 0.5 — narrow peak."},
]
BOUNDS  = {"mean": (-5, 5, 0.1), "stddev": (0.5, 3, 0.1), "n": (10, 200, 1), "bins": (5, 25, 1)}
FORMULA = lambda mean, stddev, **_kw: f"N(μ={mean:.2f}, σ²={stddev**2:.2f})"


# ── helpers ──────────────────────────────────────────────────────────────

def _linspace(a, b, n):
    if n < 2:
        return [a]
    step = (b - a) / (n - 1)
    return [a + i * step for i in range(n)]


def _clamp(x, lo, hi):
    return max(lo, min(hi, x))


# ── inverse normal CDF (probit) via Peter Acklam's rational approximation ──

_A = [-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02,
      1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00]
_B = [-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02,
      6.680131188771972e+01, -1.328068155288572e+01]
_C = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00,
     -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00]
_D = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00,
     3.754408661907416e+00]


def _probit(p):
    """Approximate inverse normal CDF using Acklam's rational algorithm."""
    if p <= 0 or p >= 1:
        return float("nan")
    if p < 0.02425:
        q = math.sqrt(-2.0 * math.log(p))
        num = ((((_C[0]*q + _C[1])*q + _C[2])*q + _C[3])*q + _C[4])*q + _C[5]
        den = ((((_D[0]*q + _D[1])*q + _D[2])*q + _D[3])*q + 1.0)
        return num / den
    if p <= 0.97575:
        q = p - 0.5
        r = q * q
        num = ((((_A[0]*r + _A[1])*r + _A[2])*r + _A[3])*r + _A[4])*r + _A[5]
        den = ((((_B[0]*r + _B[1])*r + _B[2])*r + _B[3])*r + _B[4])*r + 1.0
        return num * q / den
    q = math.sqrt(-2.0 * math.log(1.0 - p))
    num = ((((_C[0]*q + _C[1])*q + _C[2])*q + _C[3])*q + _C[4])*q + _C[5]
    den = ((((_D[0]*q + _D[1])*q + _D[2])*q + _D[3])*q + 1.0)
    return -num / den


def _normal_pdf(x, mean, stddev):
    """Probability density function of the normal distribution."""
    z = (x - mean) / stddev
    return (1.0 / (stddev * math.sqrt(2.0 * math.pi))) * math.exp(-0.5 * z * z)


# ── percentile helper ───────────────────────────────────────────────────

def _percentile(sorted_data, p):
    """Linear interpolation of the p-th percentile of sorted_data."""
    n = len(sorted_data)
    if n == 0:
        return 0.0
    if n == 1:
        return sorted_data[0]
    k = (p / 100.0) * (n - 1)
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return sorted_data[int(k)]
    d0 = sorted_data[int(f)] * (c - k)
    d1 = sorted_data[int(c)] * (k - f)
    return d0 + d1


# ── public compute() ─────────────────────────────────────────────────────

def compute(mean, stddev, n, bins):
    """Generate a deterministic normal sample and compute summary statistics.

    Returns a flat dict with 'data', 'sample_mean', 'sample_std',
    'variance', 'median', 'q1', 'q3', 'iqr', 'data_min', 'data_max',
    'data_range', 'bin_edges', 'bin_counts', 'pdf_x', 'pdf_y',
    and the input params.
    """
    # Clamp inputs
    n = int(_clamp(n, 5, 500))
    bins = int(_clamp(bins, 3, 50))

    # Generate deterministic normal data via quantiles (Acklam probit).
    data = []
    for i in range(n):
        p = (i + 0.5) / n
        z = _probit(p)
        data.append(mean + stddev * z)

    # Summary stats
    sorted_data = sorted(data)
    sample_mean = sum(data) / n
    variance = sum((x - sample_mean) ** 2 for x in data) / (n - 1)
    sample_std = math.sqrt(variance)
    median = _percentile(sorted_data, 50)
    q1 = _percentile(sorted_data, 25)
    q3 = _percentile(sorted_data, 75)
    iqr = q3 - q1
    data_min = sorted_data[0]
    data_max = sorted_data[-1]
    data_range = data_max - data_min

    # Histogram bins
    if data_max - data_min < 1e-12:
        bin_edges = [data_min - 0.5 + i for i in range(bins + 1)]
    else:
        pad = (data_max - data_min) * 0.05
        bin_edges = _linspace(data_min - pad, data_max + pad, bins + 1)
    bin_counts = [0] * bins
    for d in data:
        for j in range(bins):
            if bin_edges[j] <= d < bin_edges[j + 1]:
                bin_counts[j] += 1
                break
        if abs(d - bin_edges[-1]) < 1e-12:
            bin_counts[-1] += 1

    # PDF curve (evaluate over a nice range)
    xmin = mean - 4.5 * stddev
    xmax = mean + 4.5 * stddev
    pdf_x = _linspace(xmin, xmax, 300)
    pdf_y = [_normal_pdf(x, mean, stddev) for x in pdf_x]

    # Theoretical values within 1σ / 2σ
    within_1sigma = sum(1 for d in data if mean - stddev <= d <= mean + stddev)
    within_2sigma = sum(1 for d in data if mean - 2 * stddev <= d <= mean + 2 * stddev)

    return {
        "mean": mean,
        "stddev": stddev,
        "n": n,
        "bins": bins,
        "data": data,
        "sorted_data": sorted_data,
        "sample_mean": sample_mean,
        "sample_std": sample_std,
        "variance": variance,
        "median": median,
        "q1": q1,
        "q3": q3,
        "iqr": iqr,
        "data_min": data_min,
        "data_max": data_max,
        "data_range": data_range,
        "bin_edges": bin_edges,
        "bin_counts": bin_counts,
        "pdf_x": pdf_x,
        "pdf_y": pdf_y,
        "within_1sigma": within_1sigma,
        "within_2sigma": within_2sigma,
        "pct_1sigma": 100.0 * within_1sigma / n,
        "pct_2sigma": 100.0 * within_2sigma / n,
    }


def _fmt(x, nd=3):
    s = f"{x:.{nd}f}"
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return s or "0"


def steps(mean, stddev, n, bins, sample_mean, sample_std, variance,
          median, q1, q3, iqr, data_range, pct_1sigma, pct_2sigma,
          **_ignored):
    return [
        {"text": "The normal distribution is defined by its mean μ and standard deviation σ.",
         "formula": "X ∼ N(μ, σ²)",
         "result": f"N(μ={_fmt(mean)}, σ²={_fmt(stddev**2)})"},
        {"text": "Generate n evenly-spaced quantile samples from the distribution.",
         "result": f"n = {n} data points"},
        {"text": "The sample mean estimates the centre of the distribution.",
         "formula": "x̄ = (1/n) Σ xᵢ",
         "result": f"x̄ = {_fmt(sample_mean)}",
         "result_bind": ("mean", float(mean))},
        {"text": "The sample variance and standard deviation measure spread.",
         "formula": "s² = Σ(xᵢ − x̄)² / (n−1)",
         "result": f"s² = {_fmt(variance)},  s = {_fmt(sample_std)}",
         "result_bind": ("stddev", float(stddev))},
        {"text": "The median is the 50th percentile.",
         "result": f"median = {_fmt(median)}"},
        {"text": "Quartiles Q₁ and Q₃ show the middle 50 % spread.",
         "result": f"Q₁ = {_fmt(q1)},  Q₃ = {_fmt(q3)},  IQR = {_fmt(iqr)}"},
        {"text": "In a normal distribution, roughly 68 % of data falls within 1σ and 95 % within 2σ.",
         "result": f"Within 1σ: {_fmt(pct_1sigma, 1)} %,  Within 2σ: {_fmt(pct_2sigma, 1)} %"},
    ]


def solvers(_params=None):
    from math import sqrt
    return {
        "vars": [
            {"symbol": "μ", "label": "mean", "color": "#3b82f6"},
            {"symbol": "σ", "label": "std. dev.", "color": "#a855f7"},
            {"symbol": "x", "label": "data point", "color": "#06b6d4"},
            {"symbol": "z", "label": "z-score", "color": "#f97316"},
        ],
        "solvers": {
            "z": {"formula": "z = (x − μ) / σ", "compute_js": "(x - μ) / σ"},
            "x": {"formula": "x = μ + z·σ",     "compute_js": "μ + z * σ"},
        },
    }
