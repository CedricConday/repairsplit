"""Seeded trial simulator with a known answer.

Every simulated participant has a stable true level, measurement noise on every
visit, and a true individual response to treatment that the simulator knows and
the analysis does not. A share of participants are responders with a fixed
effect; the rest have none. A share of 0 or 1 means everyone responds the same,
which is the "no individual differences" case.

Parameters (all in outcome units, e.g. ms of P100 latency):
  responder_share   expected fraction of participants who respond
  responder_effect  effect in responders (negative = latency shortens)
  between_sd        SD of true levels between people
  noise_sd          SD of one measurement around a person's true level; a
                    change score between two visits has SD sqrt(2) * noise_sd
  moderator_corr    0 = responders are a random subset; 1 = responders are
                    exactly the people with the highest `age`
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy import stats

NOISE_KINDS = ("normal", "t5")


@dataclass(frozen=True)
class Scenario:
    design: str  # "parallel" or "crossover"
    n: int
    responder_share: float
    responder_effect: float
    between_sd: float
    noise_sd: float
    moderator_corr: float = 0.0
    baseline_mean: float = 0.0
    period_effect: float = 0.0
    carryover: float = 0.0
    noise: str = "normal"
    n_treated: int | None = None  # parallel: defaults to n // 2; crossover: treatment-first group

    def __post_init__(self):
        if self.design not in ("parallel", "crossover"):
            raise ValueError("design must be 'parallel' or 'crossover'")
        if not 0.0 <= self.responder_share <= 1.0:
            raise ValueError("responder_share must be between 0 and 1")
        if self.noise not in NOISE_KINDS:
            raise ValueError(f"noise must be one of {NOISE_KINDS}")
        if self.n < 8:
            raise ValueError("n must be at least 8")

    @property
    def n_first(self) -> int:
        return self.n // 2 if self.n_treated is None else self.n_treated

    @property
    def true_sd_ir(self) -> float:
        p = self.responder_share
        return abs(self.responder_effect) * float(np.sqrt(p * (1 - p)))

    @property
    def true_mean_effect(self) -> float:
        return self.responder_share * self.responder_effect


def _noise(rng, kind, shape):
    if kind == "normal":
        return rng.standard_normal(shape)
    return rng.standard_t(5, size=shape) / np.sqrt(5.0 / 3.0)  # unit variance


def draw(sc: Scenario, n_sims: int, rng: np.random.Generator) -> dict:
    """Draw n_sims trials. Arrays have shape (n_sims, n); the first n_first
    columns are the treated arm (parallel) or the treatment-first group."""
    shape = (n_sims, sc.n)
    z_age = rng.standard_normal(shape)
    latent = sc.moderator_corr * z_age + np.sqrt(1 - sc.moderator_corr**2) * rng.standard_normal(
        shape
    )
    responder = latent > stats.norm.ppf(1.0 - sc.responder_share)
    response = np.where(responder, sc.responder_effect, 0.0)
    level = sc.baseline_mean + sc.between_sd * rng.standard_normal(shape)
    e0, e1, e2 = (sc.noise_sd * _noise(rng, sc.noise, shape) for _ in range(3))
    first = np.zeros(shape, dtype=bool)
    first[:, : sc.n_first] = True
    out = {
        "age": 40.0 + 8.0 * z_age,
        "responder": responder,
        "baseline": level + e0,
        "first": first,
    }
    if sc.design == "parallel":
        out["outcome"] = level + np.where(first, response, 0.0) + e1
    else:
        # `first` = treatment in period 1, control in period 2.
        y1 = level + np.where(first, response, 0.0) + e1
        y2 = (
            level
            + sc.period_effect
            + np.where(first, sc.carryover * response, response)
            + e2
        )
        out["period1"], out["period2"] = y1, y2
    return out


def simulate_trial(sc: Scenario, seed: int = 0) -> pd.DataFrame:
    """One simulated trial in the tidy CSV layout that `repairsplit analyze` reads.

    The extra column `true_responder` is the known answer. `analyze` ignores it.
    """
    d = draw(sc, 1, np.random.default_rng(seed))
    ids = [f"P{i + 1:04d}" for i in range(sc.n)]
    first = d["first"][0]
    common = {
        "participant": ids,
        "baseline": d["baseline"][0],
        "age": d["age"][0],
        "true_responder": d["responder"][0].astype(int),
    }
    if sc.design == "parallel":
        df = pd.DataFrame(
            {
                **common,
                "arm": np.where(first, "treatment", "control"),
                "sequence": "",
                "period": 1,
                "outcome": d["outcome"][0],
            }
        )
    else:
        seq = np.where(first, "TC", "CT")
        parts = [
            pd.DataFrame({**common, "arm": "", "sequence": seq, "period": p, "outcome": d[k][0]})
            for p, k in ((1, "period1"), (2, "period2"))
        ]
        df = pd.concat(parts, ignore_index=True).sort_values(["participant", "period"])
    cols = [
        "participant", "arm", "sequence", "period", "baseline", "outcome", "age", "true_responder",
    ]
    return df[cols].reset_index(drop=True)
