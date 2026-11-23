"""Known-answer test: false-positive rate and power of every method.

Units are standardised. One measurement has noise SD 1, so a change score (or a
crossover difference) has noise SD sqrt(2). Responder effects are given in
multiples of that change-score SD.

    python scripts/known_answer.py --out results/known_answer.csv

Takes a few minutes on four cores. Every cell is seeded.
"""

from __future__ import annotations

import argparse
import itertools
import time
from multiprocessing import Pool

import numpy as np
import pandas as pd

from repairsplit.power import rejection_rates
from repairsplit.simulate import Scenario

SIZES = (30, 60, 100, 200, 500)
CHANGE_SD = float(np.sqrt(2.0))
RETEST_DF = 38


def cells():
    out = []
    for design, n in itertools.product(("parallel", "crossover"), SIZES):
        base = dict(design=design, n=n, between_sd=3.0, noise_sd=1.0)
        # No individual differences: nobody responds, or everybody responds the same.
        out.append(("uniform", 0.0, dict(base, responder_share=0.0, responder_effect=0.0)))
        everyone = dict(base, responder_share=1.0, responder_effect=-2 * CHANGE_SD)
        out.append(("uniform", 2.0, everyone))
        out.append(("uniform_heavy_tails", 2.0, dict(everyone, noise="t5")))
        for share, k in itertools.product((0.25, 0.5), (1.0, 2.0, 3.0)):
            kw = dict(base, responder_share=share, responder_effect=-k * CHANGE_SD)
            out.append(("responders_random", k, kw))
            if share == 0.5:
                out.append(("responders_tied_to_age", k, dict(kw, moderator_corr=0.7)))
    return out


def run(args):
    i, kind, k, kw, n_sims, null_draws = args
    sc = Scenario(**kw)
    r = rejection_rates(sc, n_sims=n_sims, seed=1000 + i, retest_df=RETEST_DF,
                        null_draws=null_draws)
    return {
        "design": sc.design, "n": sc.n, "kind": kind, "responder_share": sc.responder_share,
        "effect_in_change_sd": k, "noise": sc.noise, "moderator_corr": sc.moderator_corr,
        "true_sd_ir_in_change_sd": sc.true_sd_ir / CHANGE_SD, **r,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="results/known_answer.csv")
    ap.add_argument("--n-sims", type=int, default=2000)
    ap.add_argument("--null-draws", type=int, default=4000)
    ap.add_argument("--workers", type=int, default=3)
    a = ap.parse_args()
    tasks = [(i, kind, k, kw, a.n_sims, a.null_draws) for i, (kind, k, kw) in enumerate(cells())]
    t0 = time.time()
    rows = []
    with Pool(a.workers) as pool:
        for j, row in enumerate(pool.imap_unordered(run, tasks), 1):
            rows.append(row)
            print(f"{j}/{len(tasks)} {row['design']} n={row['n']} {row['kind']} "
                  f"{time.time() - t0:.0f}s", flush=True)
    df = pd.DataFrame(rows).sort_values(
        ["design", "kind", "responder_share", "effect_in_change_sd", "n"]
    )
    df.to_csv(a.out, index=False, float_format="%.4f")
    print(f"wrote {a.out} ({len(df)} cells, {a.n_sims} trials each) in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
