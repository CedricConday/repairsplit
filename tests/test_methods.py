import numpy as np
import pandas as pd
import pytest
import statsmodels.api as sm
from scipy import stats

from repairsplit import mixture
from repairsplit.crossover import analyze_differences, period_adjusted_differences
from repairsplit.moderators import (
    TooManyModerators,
    interaction_p_crossover,
    interaction_p_parallel,
    moderators_crossover,
    moderators_parallel,
)
from repairsplit.variance import brown_forsythe_p, sd_ir, sd_ir_from_summary


def test_sd_ir_summary_known_values():
    r = sd_ir_from_summary(5.0, 31, 3.0, 31)
    assert r.variance_difference == pytest.approx(16.0)
    assert r.sd_ir == pytest.approx(4.0)
    se = np.sqrt(2 * 625 / 30 + 2 * 81 / 30)
    assert r.sd_ir_ci_high == pytest.approx(np.sqrt(16 + 1.959964 * se), rel=1e-5)
    assert r.variance_ratio == pytest.approx(25 / 9)
    assert r.p_f_one_sided == pytest.approx(stats.f.sf(25 / 9, 30, 30))


def test_sd_ir_negative_difference_keeps_sign():
    r = sd_ir_from_summary(3.0, 30, 5.0, 30)
    assert r.sd_ir == pytest.approx(-4.0)
    assert r.p_f_one_sided > 0.5


def test_sd_ir_recovers_truth_in_a_large_sample():
    rng = np.random.default_rng(1)
    control = rng.normal(0, 4, 40000)
    treated = rng.normal(0, 4, 40000) + rng.normal(-2, 3, 40000)
    r = sd_ir(treated, control)
    assert r.sd_ir == pytest.approx(3.0, abs=0.15)
    assert r.sd_ir_ci_low < 3.0 < r.sd_ir_ci_high


def test_brown_forsythe_matches_scipy_levene():
    rng = np.random.default_rng(2)
    a, b = rng.normal(0, 2, 25), rng.normal(0, 1, 31)
    t, p_one = brown_forsythe_p(a, b)
    w, p_two = stats.levene(a, b, center="median")
    assert t**2 == pytest.approx(w)
    assert 2 * min(p_one, 1 - p_one) == pytest.approx(p_two)
    assert p_one < 0.5  # a is the more variable sample


def test_crossover_plain_reports_bound_not_estimate():
    rng = np.random.default_rng(3)
    r = analyze_differences(rng.normal(-2, 4, 25), rng.normal(-2, 4, 25))
    assert not r.sd_ir_estimable
    assert r.sd_ir is None and r.p_response_variance is None
    assert r.sd_ir_upper_bound == pytest.approx(r.sd_difference)
    assert r.sd_ir_upper_bound_conf_limit > r.sd_ir_upper_bound
    assert "cannot separate" in r.statement


def test_crossover_effect_period_and_retest_subtraction():
    rng = np.random.default_rng(4)
    n = 20000
    response = rng.normal(-3, 2, 2 * n)  # true SD of individual response = 2
    noise = rng.normal(0, 5, 2 * n)  # SD of a difference of two noisy measurements
    period = 1.5  # period 2 minus period 1
    d_tc = response[:n] - period + noise[:n]
    d_ct = response[n:] + period + noise[n:]
    plain = analyze_differences(d_tc, d_ct)
    assert plain.mean_effect == pytest.approx(-3.0, abs=0.1)
    assert plain.period_effect == pytest.approx(1.5, abs=0.1)
    assert plain.sd_difference == pytest.approx(np.sqrt(29), abs=0.1)
    known = analyze_differences(d_tc, d_ct, retest_sd_difference=5.0)
    assert known.sd_ir == pytest.approx(2.0, abs=0.2)
    assert known.sd_ir_ci_low < 2.0 < known.sd_ir_ci_high
    est = analyze_differences(d_tc, d_ct, retest_sd_difference=5.0, retest_df=38)
    assert est.sd_ir == pytest.approx(known.sd_ir)
    # An outside estimate from 39 people is far less certain than a known value.
    assert est.sd_ir_ci_high - est.sd_ir_ci_low > known.sd_ir_ci_high - known.sd_ir_ci_low
    assert est.p_response_variance > known.p_response_variance


def test_period_adjustment_removes_period_effect():
    a, b = period_adjusted_differences(np.array([1.0, 3.0]), np.array([7.0, 9.0]))
    assert a.mean() == pytest.approx(5.0) and b.mean() == pytest.approx(5.0)


def test_mixture_separated_groups_detected_single_group_not():
    rng = np.random.default_rng(5)
    two = np.concatenate([rng.normal(0, 1, 40), rng.normal(6, 1, 40)])
    r = mixture.mixture_check(two, n_bootstrap=199, fpr_sims=0)
    assert r.p_bootstrap <= 0.01
    assert r.mean_low == pytest.approx(0, abs=0.6) and r.mean_high == pytest.approx(6, abs=0.6)
    assert r.weight_low == pytest.approx(0.5, abs=0.1)
    one = mixture.mixture_check(rng.normal(0, 1, 80), n_bootstrap=199, fpr_sims=0)
    assert one.p_bootstrap > 0.05
    assert one.false_positive_rate_heavy_tailed is None


def test_mixture_statistic_is_location_scale_invariant():
    rng = np.random.default_rng(6)
    x = rng.normal(0, 1, (5, 40))
    a = mixture.em_lrt(x)[0]
    b = mixture.em_lrt(120 + 7.5 * x)[0]
    assert np.allclose(a, b, atol=1e-6)


def test_bootstrap_p_agrees_with_critical_value_shortcut():
    # The power simulations compare the statistic with a null critical value
    # instead of bootstrapping every trial. Both must make the same call.
    rng = np.random.default_rng(7)
    crit = mixture.critical_value(40, 0.05, 2000)
    for _ in range(4):
        x = rng.normal(0, 1, 40) + rng.choice([0.0, 3.5], 40)
        lrt = mixture.em_lrt(x)[0][0]
        p = mixture.mixture_check(x, n_bootstrap=499, fpr_sims=0).p_bootstrap
        if abs(p - 0.05) > 0.03:  # skip borderline cases, Monte Carlo error
            assert (p < 0.05) == (lrt > crit)


def test_moderator_refusal_and_override():
    rng = np.random.default_rng(8)
    cov = pd.DataFrame(rng.normal(size=(40, 4)), columns=list("abcd"))
    y, t = rng.normal(size=40), np.repeat([1, 0], 20)
    with pytest.raises(TooManyModerators):
        moderators_parallel(y, t, cov)
    rows = moderators_parallel(y, t, cov, allow_many=True)
    assert len(rows) == 4
    assert all(r.p_adjusted >= r.p_raw for r in rows)
    with pytest.raises(TooManyModerators):
        moderators_crossover(y, t, cov[["a", "b"]], max_moderators=1)


def test_holm_correction_values():
    rng = np.random.default_rng(9)
    cov = pd.DataFrame(rng.normal(size=(60, 2)), columns=["age", "base"])
    t = np.repeat([1, 0], 30)
    y = rng.normal(size=60) + 1.2 * t * (cov["age"] - cov["age"].mean())
    rows = moderators_parallel(y, t, cov)
    p = sorted(r.p_raw for r in rows)
    adj = sorted(r.p_adjusted for r in rows)
    assert adj[0] == pytest.approx(min(1, 2 * p[0]))
    assert adj[1] == pytest.approx(max(adj[0], p[1]))
    assert next(r for r in rows if r.moderator == "age").reject


def test_batch_interaction_matches_statsmodels():
    rng = np.random.default_rng(10)
    c, y = rng.normal(size=50), rng.normal(size=50)
    t = np.repeat([1.0, 0.0], 25)
    cc = c - c.mean()
    X = np.column_stack([np.ones(50), t, cc, t * cc])
    assert interaction_p_parallel(y[:25], c[:25], y[25:], c[25:]) == pytest.approx(
        sm.OLS(y, X).fit().pvalues[3]
    )
    X2 = np.column_stack([np.ones(50), t, cc])
    assert interaction_p_crossover(y[:25], c[:25], y[25:], c[25:]) == pytest.approx(
        sm.OLS(y, X2).fit().pvalues[2]
    )
    rows = moderators_crossover(y, t, pd.DataFrame({"c": c}))
    assert rows[0].p_raw == pytest.approx(sm.OLS(y, X2).fit().pvalues[2])
