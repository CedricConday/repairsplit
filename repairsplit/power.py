"""Rejection rates of each method over many simulated trials.

When the scenario has no individual differences (responder share 0 or 1) the
rate is the false-positive rate. Otherwise it is the power.

All variance tests are one-sided at alpha: the question is whether treatment
ADDS spread.
"""

from __future__ import annotations

import numpy as np

from . import mixture
from .crossover import period_adjusted_differences, pooled_difference_variance, retest_p
from .moderators import interaction_p_crossover, interaction_p_parallel
from .simulate import Scenario, draw
from .variance import brown_forsythe_p, f_test_p, var_diff_ci

PARALLEL_METHODS = ("variance_ratio_f", "brown_forsythe", "mixture_blrt", "moderators_holm")
CROSSOVER_METHODS = ("retest_f", "retest_known", "mixture_blrt", "moderators_holm")


def rejection_rates(
    sc: Scenario,
    n_sims: int = 2000,
    seed: int = 0,
    alpha: float = 0.05,
    retest_df: int = 38,
    null_draws: int = 4000,
) -> dict:
    """Share of simulated trials in which each method rejects at level alpha.

    Parallel: variance-ratio F test, Brown-Forsythe test, mixture bootstrap LRT on
    treated-arm change scores, and two pre-specified moderators (age, baseline)
    with Holm correction (rejects if either does).

    Crossover: the same mixture and moderator checks on within-person differences,
    plus the outside-noise test in two forms. `retest_f` draws a fresh outside
    noise estimate with `retest_df` degrees of freedom for every trial, as a real
    test-retest study would give. `retest_known` treats the noise as known
    exactly, an upper limit on what outside information can deliver. The plain
    crossover has no test of response variance at all, so there is no row for it.
    """
    rng = np.random.default_rng([seed, sc.n, n_sims])
    d = draw(sc, n_sims, rng)
    k = sc.n_first
    out: dict = {"n_sims": n_sims}

    if sc.design == "parallel":
        change = d["outcome"] - d["baseline"]
        xt, xc = change[:, :k], change[:, k:]
        vt, vc = xt.var(axis=1, ddof=1), xc.var(axis=1, ddof=1)
        dft, dfc = xt.shape[1] - 1, xc.shape[1] - 1
        out["variance_ratio_f"] = float(np.mean(f_test_p(vt, dft, vc, dfc) < alpha))
        out["brown_forsythe"] = float(np.mean(brown_forsythe_p(xt, xc)[1] < alpha))
        diff, lo, hi = var_diff_ci(vt, dft, vc, dfc)
        truth = sc.true_sd_ir**2
        out["sd_ir_ci_coverage"] = float(np.mean((lo <= truth) & (truth <= hi)))
        out["mean_variance_difference"] = float(diff.mean())
        out["true_variance_difference"] = truth
        crit = mixture.critical_value(xt.shape[1], alpha, null_draws)
        out["mixture_blrt"] = float(np.mean(mixture.em_lrt(xt)[0] > crit))
        p_mod = np.minimum(
            interaction_p_parallel(xt, d["age"][:, :k], xc, d["age"][:, k:]),
            interaction_p_parallel(xt, d["baseline"][:, :k], xc, d["baseline"][:, k:]),
        )
        out["moderators_holm"] = float(np.mean(p_mod < alpha / 2))
        return out

    diff = np.where(d["first"], d["period1"] - d["period2"], d["period2"] - d["period1"])
    d_tc, d_ct = diff[:, :k], diff[:, k:]
    var_d, df = pooled_difference_variance(d_tc, d_ct)
    noise_var = 2.0 * sc.noise_sd**2
    ext = noise_var * rng.chisquare(retest_df, size=n_sims) / retest_df
    out["retest_f"] = float(np.mean(retest_p(var_d, df, ext, retest_df) < alpha))
    out["retest_known"] = float(np.mean(retest_p(var_d, df, noise_var) < alpha))
    out["mean_variance_difference"] = float(np.mean(var_d - noise_var))
    out["true_variance_difference"] = sc.true_sd_ir**2
    a_tc, a_ct = period_adjusted_differences(d_tc, d_ct)
    adj = np.concatenate([a_tc, a_ct], axis=1)
    crit = mixture.critical_value(sc.n, alpha, null_draws)
    out["mixture_blrt"] = float(np.mean(mixture.em_lrt(adj)[0] > crit))
    p_mod = np.minimum(
        interaction_p_crossover(d_tc, d["age"][:, :k], d_ct, d["age"][:, k:]),
        interaction_p_crossover(d_tc, d["baseline"][:, :k], d_ct, d["baseline"][:, k:]),
    )
    out["moderators_holm"] = float(np.mean(p_mod < alpha / 2))
    return out
