"""What could the published trial designs have detected?

Reads scripts/trial_inputs.json (every number cited or marked as an assumption)
and simulates trials of the published size.

For each trial, mean effect and SD of change, three splits with the same mean:
  uniform   everyone shifts by the mean effect (false-positive rate)
  half      half the participants respond with twice the mean effect
  quarter   a quarter respond with four times the mean effect

Then, per trial, the responder effect a half split would need for 80% power.

    python scripts/trial_designs.py --out results/trial_designs.csv
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from repairsplit.power import CROSSOVER_METHODS, PARALLEL_METHODS, rejection_rates
from repairsplit.simulate import Scenario
from repairsplit.variance import sd_ir_from_summary

HERE = Path(__file__).parent
SPLITS = (("uniform", 1.0), ("half", 0.5), ("quarter", 0.25))
MULTIPLES = (1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 5.0, 6.0)


def rates(design, n, n_first, share, effect, sd_change, rho, n_sims, seed, retest_df):
    sc = Scenario(
        design=design, n=n, n_treated=n_first, responder_share=share, responder_effect=effect,
        between_sd=3.0 * sd_change, noise_sd=sd_change / np.sqrt(2.0), moderator_corr=rho,
    )
    return rejection_rates(sc, n_sims=n_sims, seed=seed, retest_df=retest_df)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="results/trial_designs.csv")
    ap.add_argument("--n-sims", type=int, default=4000)
    a = ap.parse_args()
    inp = json.loads((HERE / "trial_inputs.json").read_text())
    retest_df = inp["noise"]["retest_df"]["value"]
    rho = inp["moderator_assumption"]["moderator_corr"]
    rows, need = [], []
    seed = 5000
    for name, t in inp["trials"].items():
        methods = CROSSOVER_METHODS if t["design"] == "crossover" else PARALLEL_METHODS
        for eff in t["effects"]:
            for sd in t["sd_sweep"]:
                for split, share in SPLITS:
                    seed += 1
                    kw = dict(design=t["design"], n=t["n"], n_first=t["n_first"], share=share,
                              effect=eff["value"] / share, sd_change=sd, n_sims=a.n_sims,
                              retest_df=retest_df)
                    r = rates(**kw, rho=0.0, seed=seed)
                    tied = rates(**kw, rho=rho, seed=seed + 100000)
                    row = {
                        "trial": name, "design": t["design"], "n": t["n"],
                        "mean_effect": eff["value"], "effect_label": eff["label"],
                        "sd_change": sd, "split": split, "responder_share": share,
                        "responder_effect": eff["value"] / share,
                        "true_sd_ir": abs(eff["value"] / share) * np.sqrt(share * (1 - share)),
                    }
                    for m in methods:
                        row[m] = r[m]
                    row["moderators_holm_random"] = row.pop("moderators_holm")
                    row["moderators_holm_tied"] = tied["moderators_holm"]
                    rows.append(row)
                    print(row, flush=True)
        # Responder effect needed, half split, middle SD of the sweep.
        sd = t["sd_sweep"][len(t["sd_sweep"]) // 2]
        reached = {m: None for m in methods if m != "moderators_holm"}
        for k in MULTIPLES:
            seed += 1
            r = rates(t["design"], t["n"], t["n_first"], 0.5, -k * sd, sd, 0.0, a.n_sims, seed,
                      retest_df)
            for m in reached:
                if reached[m] is None and r[m] >= 0.8:
                    reached[m] = k
        for m, k in reached.items():
            need.append({
                "trial": name, "design": t["design"], "n": t["n"], "sd_change": sd, "method": m,
                "responder_effect_for_80pct_power_in_sd": k,
                "responder_effect_for_80pct_power": None if k is None else k * sd,
                "largest_multiple_tried": MULTIPLES[-1],
            })
    out = Path(a.out)
    pd.DataFrame(rows).to_csv(out, index=False, float_format="%.4f")
    pd.DataFrame(need).to_csv(out.with_name("trial_detectable_effect.csv"), index=False,
                              float_format="%.4f")

    # Summary-statistic check on the one trial that published change SDs per arm
    # for independent participants.
    s = sd_ir_from_summary(0.98, 26, 0.84, 26)
    summary = {
        "CCMR One lesional MTR, published SDs of change (pu)": {
            **s.to_dict(),
            "caveat": "26 analysed per arm is assumed; the abstract gives the number randomised.",
        },
        "ReBUILD VEP, registry SDs of change per eye (ms)": {
            "sd_treated_periods": 6.85, "sd_placebo_periods": 3.86, "eyes": 93,
            "variance_ratio": 6.85**2 / 3.86**2,
            "sqrt_of_variance_difference": float(np.sqrt(6.85**2 - 3.86**2)),
            "caveat": "Descriptive only. No test or interval is given, because the two columns "
            "hold the same 50 people, two eyes per person, periods of 90 and 60 days, and one "
            "group had placebo after treatment. None of the tests here is valid for that.",
        },
    }
    out.with_name("summary_statistic_checks.json").write_text(json.dumps(summary, indent=2) + "\n")
    print("done")


if __name__ == "__main__":
    main()
