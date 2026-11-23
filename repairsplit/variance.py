"""Variance-based methods for a two-arm parallel trial.

The idea (Atkinson and Batterham 2015; Hopkins 2015; Senn 2016): in a parallel
trial nobody is seen under both treatments, so an individual's response is never
observed. What is observed is the spread of change scores in each arm. Under the
model

    change in control arm   = natural change + noise
    change in treated arm   = natural change + noise + individual response

with the individual response independent of the rest, the variance of individual
response is the difference of the two change-score variances. If everyone
responds the same, the two variances are equal.

All functions work on arrays whose last axis is "participants", so the same code
analyses one trial or many simulated trials at once.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np
from scipy import stats


def signed_sqrt(x):
    """Square root that keeps the sign: -4 becomes -2.

    A negative variance difference means the treated arm was *less* variable than
    the control arm. Reporting it as a negative SD keeps that visible instead of
    hiding it behind a zero.
    """
    x = np.asarray(x, dtype=float)
    return np.sign(x) * np.sqrt(np.abs(x))


@dataclass
class SDIRResult:
    n_treated: int
    n_control: int
    sd_treated: float
    sd_control: float
    variance_difference: float
    sd_ir: float
    ci_level: float
    sd_ir_ci_low: float
    sd_ir_ci_high: float
    variance_ratio: float
    variance_ratio_ci_low: float
    variance_ratio_ci_high: float
    p_f_one_sided: float
    p_f_two_sided: float

    def to_dict(self) -> dict:
        return asdict(self)


def var_diff_ci(var_t, df_t, var_c, df_c, level: float = 0.95):
    """Normal-approximation confidence interval for var_t - var_c.

    Uses the sampling variance of a normal sample variance, 2 * sigma^4 / df.
    Returns (difference, low, high) on the variance scale.
    """
    var_t = np.asarray(var_t, dtype=float)
    var_c = np.asarray(var_c, dtype=float)
    diff = var_t - var_c
    se = np.sqrt(2.0 * var_t**2 / df_t + 2.0 * var_c**2 / df_c)
    z = stats.norm.ppf(0.5 + level / 2.0)
    return diff, diff - z * se, diff + z * se


def f_test_p(var_t, df_t, var_c, df_c):
    """One-sided p-value for 'treated variance is larger' from the F distribution."""
    ratio = np.asarray(var_t, dtype=float) / np.asarray(var_c, dtype=float)
    return stats.f.sf(ratio, df_t, df_c)


def sd_ir_from_summary(
    sd_treated: float, n_treated: int, sd_control: float, n_control: int, level: float = 0.95
) -> SDIRResult:
    """SD of individual response from published change-score SDs and group sizes."""
    if n_treated < 3 or n_control < 3:
        raise ValueError("need at least 3 participants per arm")
    vt, vc = sd_treated**2, sd_control**2
    dft, dfc = n_treated - 1, n_control - 1
    diff, lo, hi = var_diff_ci(vt, dft, vc, dfc, level)
    ratio = vt / vc
    a = (1.0 - level) / 2.0
    r_lo = ratio / stats.f.ppf(1 - a, dft, dfc)
    r_hi = ratio / stats.f.ppf(a, dft, dfc)
    p_one = float(stats.f.sf(ratio, dft, dfc))
    p_two = float(min(1.0, 2.0 * min(p_one, 1.0 - p_one)))
    return SDIRResult(
        n_treated=int(n_treated),
        n_control=int(n_control),
        sd_treated=float(sd_treated),
        sd_control=float(sd_control),
        variance_difference=float(diff),
        sd_ir=float(signed_sqrt(diff)),
        ci_level=level,
        sd_ir_ci_low=float(signed_sqrt(lo)),
        sd_ir_ci_high=float(signed_sqrt(hi)),
        variance_ratio=float(ratio),
        variance_ratio_ci_low=float(r_lo),
        variance_ratio_ci_high=float(r_hi),
        p_f_one_sided=p_one,
        p_f_two_sided=p_two,
    )


def sd_ir(change_treated, change_control, level: float = 0.95) -> SDIRResult:
    """SD of individual response from participant-level change scores."""
    xt = np.asarray(change_treated, dtype=float)
    xc = np.asarray(change_control, dtype=float)
    return sd_ir_from_summary(
        float(xt.std(ddof=1)), xt.size, float(xc.std(ddof=1)), xc.size, level
    )


def brown_forsythe_p(change_treated, change_control):
    """One-sided Brown-Forsythe test that the treated arm is more spread out.

    This is Levene's test with deviations taken from the arm median (Brown and
    Forsythe 1974). With two groups it is a pooled t-test on the absolute
    deviations, which gives a direction. It holds its error rate under
    heavy-tailed noise much better than the F test.

    Returns (t statistic, one-sided p). The usual two-sided Levene p-value is
    2 * min(p, 1 - p).
    """
    xt = np.asarray(change_treated, dtype=float)
    xc = np.asarray(change_control, dtype=float)
    zt = np.abs(xt - np.median(xt, axis=-1, keepdims=True))
    zc = np.abs(xc - np.median(xc, axis=-1, keepdims=True))
    nt, nc = zt.shape[-1], zc.shape[-1]
    df = nt + nc - 2
    pooled = ((nt - 1) * zt.var(axis=-1, ddof=1) + (nc - 1) * zc.var(axis=-1, ddof=1)) / df
    t = (zt.mean(axis=-1) - zc.mean(axis=-1)) / np.sqrt(pooled * (1.0 / nt + 1.0 / nc))
    return t, stats.t.sf(t, df)
