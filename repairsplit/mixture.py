"""Two-component mixture check: responders versus non-responders.

Fits one normal distribution and a mixture of two normals with a common
variance to the same values (treated-arm change scores in a parallel trial,
within-person treatment-minus-control differences in a crossover). The
likelihood-ratio statistic does not follow a chi-square distribution here, so
its null distribution is simulated from the fitted single normal (parametric
bootstrap; McLachlan 1987).

Because both fits are location- and scale-equivariant, the statistic's null
distribution under a normal depends only on the sample size. The power
simulations use that: one set of null draws per sample size gives the critical
value, which is the bootstrap test in the limit of many bootstrap samples.

The EM fit stops after a fixed number of steps or when the parameters stop
moving. The test stays valid whatever the stopping rule, because the null draws
go through exactly the same fit.

A common variance keeps the mixture likelihood bounded. It also means the check
is aimed at "two groups with different means", not "one group is noisier".
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache

import numpy as np

_STARTS = (0.25, 0.5, 0.75)
_MAX_ITER = 200
_TOL = 1e-5


def _loglik_mix(x, pi, m1, m2, var):
    a = np.log(pi)[:, None] - (x - m1[:, None]) ** 2 / (2 * var[:, None])
    b = np.log1p(-pi)[:, None] - (x - m2[:, None]) ** 2 / (2 * var[:, None])
    ll = np.logaddexp(a, b).sum(axis=1)
    return ll - 0.5 * x.shape[1] * np.log(2 * np.pi * var)


def em_lrt(x):
    """Likelihood-ratio statistic, two-component versus one-component normal.

    x has shape (n,) or (B, n). Returns (lrt, params) where params is a dict of
    arrays with the best mixture fit: weight of the lower component, the two
    means and the common SD.
    """
    x = np.atleast_2d(np.asarray(x, dtype=float))
    n = x.shape[1]
    if n < 8:
        raise ValueError("mixture check needs at least 8 values")
    var0 = x.var(axis=1)
    ll0 = -0.5 * n * (np.log(2 * np.pi * var0) + 1.0)
    floor = 1e-6 * var0
    xs = np.sort(x, axis=1)

    best_ll = ll0.copy()
    best = {
        "weight_low": np.ones(x.shape[0]),
        "mean_low": x.mean(axis=1),
        "mean_high": x.mean(axis=1),
        "sd": np.sqrt(var0),
    }
    scale = np.sqrt(var0)
    for q in _STARTS:
        k = min(max(int(round(q * n)), 2), n - 2)
        m1 = xs[:, :k].mean(axis=1)
        m2 = xs[:, k:].mean(axis=1)
        pi = np.full(x.shape[0], k / n)
        var = ((xs[:, :k] - m1[:, None]) ** 2).sum(1) + ((xs[:, k:] - m2[:, None]) ** 2).sum(1)
        var = np.maximum(var / n, floor)
        active = np.arange(x.shape[0])  # rows still moving; converged rows are left alone
        for _ in range(_MAX_ITER):
            xa = x[active]
            a1, a2, av, ap = m1[active, None], m2[active, None], var[active, None], pi[active]
            logit = (np.log1p(-ap) - np.log(ap))[:, None] + ((xa - a1) ** 2 - (xa - a2) ** 2) / (
                2 * av
            )
            r = 1.0 / (1.0 + np.exp(np.clip(logit, -700, 700)))
            s1 = r.sum(axis=1)
            pi_new = np.clip(s1 / n, 1e-6, 1 - 1e-6)
            m1_new = (r * xa).sum(axis=1) / np.maximum(s1, 1e-300)
            m2_new = ((1 - r) * xa).sum(axis=1) / np.maximum(n - s1, 1e-300)
            var_new = r * (xa - m1_new[:, None]) ** 2 + (1 - r) * (xa - m2_new[:, None]) ** 2
            var_new = np.maximum(var_new.sum(axis=1) / n, floor[active])
            moved = np.maximum(
                np.maximum(np.abs(m1_new - m1[active]), np.abs(m2_new - m2[active]))
                / scale[active],
                np.abs(pi_new - ap),
            )
            pi[active], m1[active], m2[active], var[active] = pi_new, m1_new, m2_new, var_new
            active = active[moved > _TOL]
            if active.size == 0:
                break
        ll = _loglik_mix(x, pi, m1, m2, var)
        better = ll > best_ll
        best_ll = np.where(better, ll, best_ll)
        lo_is_1 = m1 <= m2
        cand = {
            "weight_low": np.where(lo_is_1, pi, 1 - pi),
            "mean_low": np.minimum(m1, m2),
            "mean_high": np.maximum(m1, m2),
            "sd": np.sqrt(var),
        }
        for key in best:
            best[key] = np.where(better, cand[key], best[key])
    lrt = np.maximum(2.0 * (best_ll - ll0), 0.0)
    return lrt, best


def null_lrt(n: int, n_draws: int, seed: int = 0, chunk: int = 500):
    """LRT values for n_draws standard-normal samples of size n."""
    rng = np.random.default_rng([seed, n, n_draws])
    out = []
    left = n_draws
    while left > 0:
        b = min(chunk, left)
        out.append(em_lrt(rng.standard_normal((b, n)))[0])
        left -= b
    return np.concatenate(out)


@lru_cache(maxsize=64)
def critical_value(n: int, alpha: float = 0.05, n_draws: int = 4000, seed: int = 0) -> float:
    """Upper-alpha point of the null LRT distribution at sample size n."""
    return float(np.quantile(null_lrt(n, n_draws, seed), 1.0 - alpha))


@dataclass
class MixtureResult:
    n: int
    lrt: float
    p_bootstrap: float
    n_bootstrap: int
    weight_low: float
    mean_low: float
    mean_high: float
    component_sd: float
    alpha: float
    false_positive_rate_normal: float
    false_positive_rate_heavy_tailed: float | None
    note: str

    def to_dict(self) -> dict:
        return asdict(self)


def heavy_tail_fpr(n: int, alpha: float = 0.05, n_sims: int = 400, seed: int = 0) -> float:
    """How often the check fires on single-group data with heavy tails.

    Draws samples of size n from a t distribution with 5 degrees of freedom (one
    group, no responders) and counts how often the statistic exceeds the
    normal-null critical value. Anything well above alpha means: with outlier-
    prone measurements, a "significant" mixture is not evidence of responders.
    """
    rng = np.random.default_rng([seed, n, 5])
    lrt = em_lrt(rng.standard_t(5, size=(n_sims, n)))[0]
    return float(np.mean(lrt > critical_value(n, alpha)))


def mixture_check(
    x,
    n_bootstrap: int = 999,
    alpha: float = 0.05,
    seed: int = 0,
    fpr_sims: int = 400,
) -> MixtureResult:
    """Bootstrap likelihood-ratio test of two components against one.

    Reports the test's false-positive rate alongside the p-value: alpha by
    construction when the noise is normal, and a simulated rate at this sample
    size when the noise is heavy-tailed (set fpr_sims=0 to skip).
    """
    x = np.asarray(x, dtype=float).ravel()
    lrt, par = em_lrt(x)
    null = null_lrt(x.size, n_bootstrap, seed=seed + 1)
    p = (1.0 + np.sum(null >= lrt[0])) / (n_bootstrap + 1.0)
    fpr_heavy = heavy_tail_fpr(x.size, alpha, fpr_sims, seed) if fpr_sims else None
    return MixtureResult(
        n=int(x.size),
        lrt=float(lrt[0]),
        p_bootstrap=float(p),
        n_bootstrap=n_bootstrap,
        weight_low=float(par["weight_low"][0]),
        mean_low=float(par["mean_low"][0]),
        mean_high=float(par["mean_high"][0]),
        component_sd=float(par["sd"][0]),
        alpha=alpha,
        false_positive_rate_normal=alpha,
        false_positive_rate_heavy_tailed=fpr_heavy,
        note=(
            "The bootstrap null is a single normal. The false-positive rate equals alpha only "
            "if single-group noise really is normal; the heavy-tailed rate shows how far it "
            "moves when it is not. The fitted component means are not estimates of who responded."
        ),
    )
