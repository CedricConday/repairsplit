"""What a two-period crossover can and cannot say about individual response.

Model for participant i in period j:

    y_ij = person_i + period_j + response_i * treated_ij + noise_ij

Each person gives one treated value and one control value. Their difference is

    d_i = response_i +/- period effect + (noise_i,treated - noise_i,control)

so, within a sequence group,

    Var(d) = Var(response) + 2 * Var(noise).

ESTIMABLE from a plain two-period crossover:
  * the mean treatment effect and the period effect;
  * Var(d), the SUM of response variance and noise variance;
  * therefore an UPPER BOUND on the SD of individual response (if noise were
    zero, all of Var(d) would be response).

NOT ESTIMABLE from a plain two-period crossover:
  * Var(response) on its own. A person who "improved more on drug" may simply
    have had two noisy measurements. Participant-by-treatment interaction is
    completely confounded with within-person noise. No analysis of the trial's
    own data can pull them apart (Senn 2001, 2016).

What breaks the confounding:
  * replicated periods (each person gets each treatment at least twice); not
    implemented in this version;
  * an OUTSIDE estimate of the noise: the SD of the difference between two
    measurements on the same untreated person, taken about as far apart as the
    two period-end measurements. Supply it and Var(response) = Var(d) - noise.
    This is only as good as the assumption that the outside study's noise
    applies to this trial's people, equipment and time gap.

Carryover is assumed absent. If the treatment effect persists into the control
period, differences shrink in the treatment-first group and Var(d) is distorted.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np
from scipy import stats

from .variance import signed_sqrt, var_diff_ci


@dataclass
class CrossoverResult:
    n: int
    n_treatment_first: int
    n_control_first: int
    mean_effect: float
    mean_effect_ci_low: float
    mean_effect_ci_high: float
    period_effect: float
    sd_difference: float
    df: int
    ci_level: float
    sd_ir_estimable: bool
    sd_ir_upper_bound: float
    sd_ir_upper_bound_conf_limit: float
    retest_sd_difference: float | None
    retest_df: float | None
    sd_ir: float | None
    sd_ir_ci_low: float | None
    sd_ir_ci_high: float | None
    p_response_variance: float | None
    statement: str

    def to_dict(self) -> dict:
        return asdict(self)


def pooled_difference_variance(d_tc, d_ct):
    """Pooled within-sequence variance of treated-minus-control differences.

    Arrays may carry leading batch axes. Returns (variance, df).
    """
    d_tc = np.asarray(d_tc, dtype=float)
    d_ct = np.asarray(d_ct, dtype=float)
    n1, n2 = d_tc.shape[-1], d_ct.shape[-1]
    df = n1 + n2 - 2
    ss = (n1 - 1) * d_tc.var(axis=-1, ddof=1) + (n2 - 1) * d_ct.var(axis=-1, ddof=1)
    return ss / df, df


def retest_p(var_d, df, retest_var, retest_df=None):
    """One-sided p-value that Var(d) exceeds the outside noise variance.

    With retest_df the outside estimate is treated as a sample variance (F test).
    Without it the noise variance is treated as known exactly (chi-square test),
    which overstates the evidence unless the outside study was very large.
    """
    ratio = np.asarray(var_d, dtype=float) / np.asarray(retest_var, dtype=float)
    if retest_df is None:
        return stats.chi2.sf(ratio * df, df)
    return stats.f.sf(ratio, df, retest_df)


def period_adjusted_differences(d_tc, d_ct):
    """Differences with the period effect removed, centred on the mean effect."""
    d_tc = np.asarray(d_tc, dtype=float)
    d_ct = np.asarray(d_ct, dtype=float)
    m1 = d_tc.mean(axis=-1, keepdims=True)
    m2 = d_ct.mean(axis=-1, keepdims=True)
    effect = (m1 + m2) / 2.0
    return d_tc - m1 + effect, d_ct - m2 + effect


def analyze_differences(
    d_tc,
    d_ct,
    retest_sd_difference: float | None = None,
    retest_df: float | None = None,
    level: float = 0.95,
) -> CrossoverResult:
    """Crossover analysis from treated-minus-control differences by sequence.

    d_tc: differences for participants who had treatment first.
    d_ct: differences for participants who had control first.
    """
    d_tc = np.asarray(d_tc, dtype=float)
    d_ct = np.asarray(d_ct, dtype=float)
    n1, n2 = d_tc.size, d_ct.size
    if n1 < 2 or n2 < 2:
        raise ValueError("need at least 2 participants in each sequence")
    m1, m2 = d_tc.mean(), d_ct.mean()
    var_d, df = pooled_difference_variance(d_tc, d_ct)
    var_d = float(var_d)
    effect = (m1 + m2) / 2.0
    se = np.sqrt(var_d / 4.0 * (1.0 / n1 + 1.0 / n2))
    tcrit = stats.t.ppf(0.5 + level / 2.0, df)
    upper_var = df * var_d / stats.chi2.ppf(1.0 - level, df)

    sd_ir = lo = hi = p = None
    estimable = retest_sd_difference is not None
    if estimable:
        nv = retest_sd_difference**2
        if retest_df is None:
            a = (1.0 - level) / 2.0
            diff = var_d - nv
            v_lo = df * var_d / stats.chi2.ppf(1 - a, df) - nv
            v_hi = df * var_d / stats.chi2.ppf(a, df) - nv
        else:
            diff, v_lo, v_hi = var_diff_ci(var_d, df, nv, retest_df, level)
        sd_ir, lo, hi = (float(signed_sqrt(v)) for v in (diff, v_lo, v_hi))
        p = float(retest_p(var_d, df, nv, retest_df))
        statement = (
            "SD of individual response is estimated by subtracting the supplied outside "
            "test-retest noise from the variance of within-person differences. It is valid "
            "only if that noise estimate applies to this trial."
        )
    else:
        statement = (
            "A plain two-period crossover cannot separate individual response from "
            "within-person noise. Only the upper bound is reported. Supply an outside "
            "test-retest SD of differences to estimate the SD of individual response."
        )
    return CrossoverResult(
        n=n1 + n2,
        n_treatment_first=n1,
        n_control_first=n2,
        mean_effect=float(effect),
        mean_effect_ci_low=float(effect - tcrit * se),
        mean_effect_ci_high=float(effect + tcrit * se),
        period_effect=float((m2 - m1) / 2.0),
        sd_difference=float(np.sqrt(var_d)),
        df=int(df),
        ci_level=level,
        sd_ir_estimable=estimable,
        sd_ir_upper_bound=float(np.sqrt(var_d)),
        sd_ir_upper_bound_conf_limit=float(np.sqrt(upper_var)),
        retest_sd_difference=retest_sd_difference,
        retest_df=retest_df,
        sd_ir=sd_ir,
        sd_ir_ci_low=lo,
        sd_ir_ci_high=hi,
        p_response_variance=p,
        statement=statement,
    )
