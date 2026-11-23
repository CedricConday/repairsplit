"""Pre-specified moderator analysis: treatment-by-covariate interactions.

A moderator is a baseline characteristic (age, baseline latency) that might go
with a larger or smaller treatment effect. Each moderator gets one linear
interaction test. P-values are corrected for the number of moderators (Holm
1979 by default).

The list of moderators must be fixed before looking at the outcome. To make
fishing harder, more than `max_moderators` are refused unless the caller says
explicitly that this is intended.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
from statsmodels.stats.multitest import multipletests

DEFAULT_MAX_MODERATORS = 3


class TooManyModerators(ValueError):
    pass


@dataclass
class ModeratorRow:
    moderator: str
    interaction: float
    std_error: float
    ci_low: float
    ci_high: float
    p_raw: float
    p_adjusted: float
    reject: bool

    def to_dict(self) -> dict:
        return asdict(self)


def check_count(moderators, max_moderators=DEFAULT_MAX_MODERATORS, allow_many=False):
    if len(set(moderators)) != len(moderators):
        raise ValueError("moderator listed twice")
    if len(moderators) > max_moderators and not allow_many:
        raise TooManyModerators(
            f"{len(moderators)} moderators requested, limit is {max_moderators}. "
            "Testing many moderators in a small trial mostly finds noise. "
            "Pass allow_many=True (CLI: --allow-many-moderators) to override."
        )


def _finish(rows, method, alpha):
    if not rows:
        return []
    reject, p_adj, _, _ = multipletests([r["p_raw"] for r in rows], alpha=alpha, method=method)
    return [
        ModeratorRow(**r, p_adjusted=float(pa), reject=bool(rj))
        for r, pa, rj in zip(rows, p_adj, reject, strict=True)
    ]


def _row(name, fit, term, level):
    lo, hi = fit.conf_int(alpha=1 - level).loc[term]
    return {
        "moderator": name,
        "interaction": float(fit.params[term]),
        "std_error": float(fit.bse[term]),
        "ci_low": float(lo),
        "ci_high": float(hi),
        "p_raw": float(fit.pvalues[term]),
    }


def moderators_parallel(
    change,
    treated,
    covariates: pd.DataFrame,
    method: str = "holm",
    alpha: float = 0.05,
    max_moderators: int = DEFAULT_MAX_MODERATORS,
    allow_many: bool = False,
    level: float = 0.95,
) -> list[ModeratorRow]:
    """One model per moderator: change ~ treated + covariate + treated:covariate.

    The interaction is the difference in treatment effect per one unit of the
    covariate. Covariates are centred, so the main effects stay interpretable.
    """
    names = list(covariates.columns)
    check_count(names, max_moderators, allow_many)
    y = np.asarray(change, dtype=float)
    t = np.asarray(treated, dtype=float)
    rows = []
    for name in names:
        c = covariates[name].to_numpy(dtype=float)
        c = c - c.mean()
        X = pd.DataFrame({"const": 1.0, "treated": t, "cov": c, "interaction": t * c})
        rows.append(_row(name, sm.OLS(y, X).fit(), "interaction", level))
    return _finish(rows, method, alpha)


def moderators_crossover(
    difference,
    treatment_first,
    covariates: pd.DataFrame,
    method: str = "holm",
    alpha: float = 0.05,
    max_moderators: int = DEFAULT_MAX_MODERATORS,
    allow_many: bool = False,
    level: float = 0.95,
) -> list[ModeratorRow]:
    """One model per moderator: difference ~ sequence + covariate.

    The within-person difference already is a treatment contrast, so the slope on
    the covariate is the treatment-by-covariate interaction. This IS estimable in
    a plain crossover, unlike the unexplained response variance.
    """
    names = list(covariates.columns)
    check_count(names, max_moderators, allow_many)
    d = np.asarray(difference, dtype=float)
    s = np.asarray(treatment_first, dtype=float)
    rows = []
    for name in names:
        c = covariates[name].to_numpy(dtype=float)
        c = c - c.mean()
        X = pd.DataFrame({"const": 1.0, "sequence": s, "interaction": c})
        rows.append(_row(name, sm.OLS(d, X).fit(), "interaction", level))
    return _finish(rows, method, alpha)


# Closed-form versions for simulation batches (last axis = participants).


def _sxx_sxy(x, y):
    xc = x - x.mean(axis=-1, keepdims=True)
    yc = y - y.mean(axis=-1, keepdims=True)
    return (xc * xc).sum(-1), (xc * yc).sum(-1), (yc * yc).sum(-1)


def interaction_p_parallel(y_t, c_t, y_c, c_c):
    """Raw p-value of the treated:covariate interaction, same model as above."""
    sxx_t, sxy_t, syy_t = _sxx_sxy(c_t, y_t)
    sxx_c, sxy_c, syy_c = _sxx_sxy(c_c, y_c)
    b_t, b_c = sxy_t / sxx_t, sxy_c / sxx_c
    rss = (syy_t - b_t * sxy_t) + (syy_c - b_c * sxy_c)
    df = y_t.shape[-1] + y_c.shape[-1] - 4
    se = np.sqrt(rss / df * (1.0 / sxx_t + 1.0 / sxx_c))
    return 2.0 * stats.t.sf(np.abs((b_t - b_c) / se), df)


def interaction_p_crossover(d_tc, c_tc, d_ct, c_ct):
    """Raw p-value of the covariate slope in difference ~ sequence + covariate."""
    sxx1, sxy1, syy1 = _sxx_sxy(c_tc, d_tc)
    sxx2, sxy2, syy2 = _sxx_sxy(c_ct, d_ct)
    sxx, sxy, syy = sxx1 + sxx2, sxy1 + sxy2, syy1 + syy2
    b = sxy / sxx
    df = d_tc.shape[-1] + d_ct.shape[-1] - 3
    se = np.sqrt((syy - b * sxy) / df / sxx)
    return 2.0 * stats.t.sf(np.abs(b / se), df)
