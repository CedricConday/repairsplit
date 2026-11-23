"""Turn the result CSVs into the markdown tables used in docs/VALIDATION.md.

    python scripts/make_tables.py > results/tables.md
"""

from __future__ import annotations

import pandas as pd

LABEL = {
    "variance_ratio_f": "Variance-ratio F test",
    "brown_forsythe": "Brown-Forsythe test",
    "retest_f": "Outside noise, estimated from 39 people",
    "retest_known": "Outside noise, known exactly",
    "mixture_blrt": "Mixture bootstrap LRT",
    "moderators_holm": "Two moderators, Holm",
}
METHODS = {
    "parallel": ["variance_ratio_f", "brown_forsythe", "mixture_blrt", "moderators_holm"],
    "crossover": ["retest_f", "retest_known", "mixture_blrt", "moderators_holm"],
}


def pct(x):
    return "n/a" if pd.isna(x) else f"{100 * x:.0f}%"


def table(header, rows):
    out = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return "\n".join(out) + "\n"


def known_answer(df):
    sizes = sorted(df["n"].unique())
    head = [f"n={n}" for n in sizes]
    for design in ("parallel", "crossover"):
        d = df[df["design"] == design]
        print(f"### {design.capitalize()} design: false-positive rate (nominal 5%)\n")
        rows = []
        cases = [
            ("nobody responds", (d.kind == "uniform") & (d.responder_share == 0)),
            ("everybody responds the same", (d.kind == "uniform") & (d.responder_share == 1)),
            ("same, heavy-tailed noise", d.kind == "uniform_heavy_tails"),
        ]
        for m in METHODS[design]:
            for name, mask in cases:
                s = d[mask].set_index("n")[m]
                rows.append([LABEL[m], name] + [pct(s[n]) for n in sizes])
        # Moderators are also null when responders exist but are unrelated to covariates.
        s = d[d.kind == "responders_random"].groupby("n")["moderators_holm"].mean()
        rows.append([LABEL["moderators_holm"], "responders exist, unrelated to covariates"]
                    + [pct(s[n]) for n in sizes])
        print(table(["Method", "Truth"] + head, rows))

        print(f"### {design.capitalize()} design: power to detect responders\n")
        rows = []
        r = d[d.kind == "responders_random"]
        for m in METHODS[design][:3]:
            for (share, k), g in r.groupby(["responder_share", "effect_in_change_sd"]):
                s = g.set_index("n")[m]
                rows.append([LABEL[m], f"{100 * share:.0f}%", f"{k:g} SD",
                             f"{g['true_sd_ir_in_change_sd'].iloc[0]:.2f} SD"]
                            + [pct(s[n]) for n in sizes])
        r = d[d.kind == "responders_tied_to_age"]
        for k, g in r.groupby("effect_in_change_sd"):
            s = g.set_index("n")["moderators_holm"]
            rows.append([LABEL["moderators_holm"] + " (responders tied to age, r=0.7)", "50%",
                         f"{k:g} SD", f"{g['true_sd_ir_in_change_sd'].iloc[0]:.2f} SD"]
                        + [pct(s[n]) for n in sizes])
        print(table(["Method", "Responder share", "Responder effect", "True SD of response"]
                    + head, rows))

    print("### Parallel design: SD of individual response, interval coverage and bias\n")
    d = df[(df.design == "parallel") & (df.noise == "normal")]
    rows = []
    for (kind, share, k), g in d.groupby(["kind", "responder_share", "effect_in_change_sd"]):
        if kind == "responders_tied_to_age":
            continue
        s = g.set_index("n")
        truth = f"{s['true_variance_difference'].iloc[0]:.2f}"
        rows.append([f"{100 * share:.0f}%", f"{k:g} SD", truth]
                    + [f"{pct(s.loc[n, 'sd_ir_ci_coverage'])} / "
                       f"{s.loc[n, 'mean_variance_difference']:.2f}" for n in sizes])
    print("Each cell: coverage of the 95% interval / mean estimated variance difference. "
          "Variances are in squared measurement-noise units.\n")
    print(table(["Responder share", "Responder effect", "True variance difference"] + head, rows))


def trials(df, need):
    for trial, g in df.groupby("trial", sort=False):
        design = g["design"].iloc[0]
        ms = [m for m in METHODS[design] if m != "moderators_holm"]
        print(f"### {trial}: {design}, n={g['n'].iloc[0]}\n")
        rows = []
        for _, r in g.iterrows():
            rows.append(
                [f"{r.mean_effect:g} ({r.effect_label})", f"{r.sd_change:g}", r.split,
                 f"{r.responder_effect:g}", f"{r.true_sd_ir:.2f}"]
                + [pct(r[m]) for m in ms]
                + [pct(r.moderators_holm_random), pct(r.moderators_holm_tied)]
            )
        print(table(
            ["Mean effect", "SD of change", "Split", "Effect in responders", "True SD of response"]
            + [LABEL[m] for m in ms]
            + ["Moderators, responders random", "Moderators, responders tied (r=0.7)"], rows))
    print("### Responder effect a half split would need for 80% power\n")
    rows = []
    for _, r in need.iterrows():
        v = r.responder_effect_for_80pct_power
        rows.append([r.trial, r.n, f"{r.sd_change:g}", LABEL[r.method],
                     f"more than {r.largest_multiple_tried * r.sd_change:g}" if pd.isna(v)
                     else f"{v:g}",
                     "not reached" if pd.isna(v)
                     else f"{r.responder_effect_for_80pct_power_in_sd:g} SD"])
    print(table(["Trial design", "n", "SD of change", "Method",
                 "Responder effect needed (outcome units)", "In SDs of change"], rows))


def main():
    print("## Known-answer tables\n")
    known_answer(pd.read_csv("results/known_answer.csv"))
    print("## Trial design tables\n")
    trials(pd.read_csv("results/trial_designs.csv"),
           pd.read_csv("results/trial_detectable_effect.csv"))


if __name__ == "__main__":
    main()
