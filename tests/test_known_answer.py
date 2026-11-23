"""Fast known-answer checks: small versions of the validation runs.

Tolerances are wide because each rate comes from a few hundred simulated trials.
The full tables are in docs/VALIDATION.md.
"""

import numpy as np
import pytest

from repairsplit.power import rejection_rates
from repairsplit.simulate import Scenario, draw, simulate_trial

KW = dict(n_sims=400, null_draws=1000)


def sc(design, n, share, effect, **kw):
    return Scenario(design, n, share, effect, between_sd=3.0, noise_sd=1.0, **kw)


def test_simulator_is_seeded_and_matches_its_parameters():
    s = sc("parallel", 60, 0.5, -4.0)
    assert simulate_trial(s, 3).equals(simulate_trial(s, 3))
    assert not simulate_trial(s, 3).equals(simulate_trial(s, 4))
    d = draw(sc("parallel", 4000, 0.25, -4.0), 5, np.random.default_rng(0))
    assert d["responder"].mean() == pytest.approx(0.25, abs=0.02)
    change = d["outcome"] - d["baseline"]
    assert change[:, 2000:].std() == pytest.approx(np.sqrt(2), abs=0.03)
    extra = change[:, :2000].var() - change[:, 2000:].var()
    assert extra == pytest.approx(16 * 0.25 * 0.75, abs=0.3)
    assert s.true_sd_ir == pytest.approx(2.0)


def test_share_zero_and_one_have_no_individual_differences():
    for share in (0.0, 1.0):
        s = sc("crossover", 200, share, -4.0)
        d = draw(s, 3, np.random.default_rng(1))
        assert d["responder"].all() == (share == 1.0)
        assert s.true_sd_ir == 0.0


@pytest.mark.parametrize("design", ["parallel", "crossover"])
@pytest.mark.parametrize("share", [0.0, 1.0])
def test_false_positive_rates_near_five_percent(design, share):
    r = rejection_rates(sc(design, 60, share, -4.0), **KW)
    methods = [k for k in r if k in (
        "variance_ratio_f", "brown_forsythe", "retest_f", "retest_known", "mixture_blrt",
        "moderators_holm",
    )]
    assert len(methods) == 4
    for m in methods:
        assert 0.01 <= r[m] <= 0.10, (m, r[m])


def test_parallel_power_for_a_large_split_in_a_large_trial():
    r = rejection_rates(sc("parallel", 300, 0.5, -4.0 * np.sqrt(2)), **KW)
    assert r["variance_ratio_f"] > 0.99
    assert r["brown_forsythe"] > 0.99
    assert r["mixture_blrt"] > 0.95
    assert r["sd_ir_ci_coverage"] > 0.80
    assert r["mean_variance_difference"] == pytest.approx(r["true_variance_difference"], rel=0.1)


def test_parallel_power_is_low_for_a_small_split_in_a_small_trial():
    r = rejection_rates(sc("parallel", 60, 0.5, -1.0 * np.sqrt(2)), **KW)
    assert r["variance_ratio_f"] < 0.5
    assert r["mixture_blrt"] < 0.2


def test_crossover_known_noise_beats_estimated_noise():
    s = sc("crossover", 60, 0.5, -2.0 * np.sqrt(2))
    r = rejection_rates(s, **KW)
    assert r["retest_known"] > r["retest_f"] > 0.3


def test_moderator_power_needs_responders_tied_to_the_covariate():
    kw = dict(design="parallel", n=200, share=0.5, effect=-3.0 * np.sqrt(2))
    random_resp = rejection_rates(sc(**kw), **KW)
    tied = rejection_rates(sc(**kw, moderator_corr=0.7), **KW)
    assert random_resp["moderators_holm"] < 0.1
    assert tied["moderators_holm"] > 0.8


def test_heavy_tailed_noise_inflates_f_test_but_not_brown_forsythe():
    r = rejection_rates(sc("parallel", 200, 1.0, -4.0, noise="t5"), **KW)
    assert r["variance_ratio_f"] > 0.10
    assert r["brown_forsythe"] < 0.09
