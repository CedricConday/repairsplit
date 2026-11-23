"""Command line: `repairsplit analyze` and `repairsplit simulate`."""

from __future__ import annotations

import argparse
import json
import sys

import pandas as pd

from . import __version__
from .analyze import FormatError, analyze, format_report
from .moderators import DEFAULT_MAX_MODERATORS, TooManyModerators
from .simulate import NOISE_KINDS, Scenario, simulate_trial


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="repairsplit",
        description="Responders versus a uniform shift in small two-arm or crossover trials. "
        "Statistics only; not medical advice.",
    )
    p.add_argument("--version", action="version", version=__version__)
    sub = p.add_subparsers(dest="command", required=True)

    a = sub.add_parser("analyze", help="analyse a tidy trial CSV")
    a.add_argument("csv")
    a.add_argument("--design", choices=["auto", "parallel", "crossover"], default="auto")
    a.add_argument("--treatment-label", default="treatment",
                   help="value of 'arm' that marks the treated arm (parallel)")
    a.add_argument("--moderators", nargs="*", default=[],
                   help="pre-specified covariate columns to test as moderators")
    a.add_argument("--max-moderators", type=int, default=DEFAULT_MAX_MODERATORS)
    a.add_argument("--allow-many-moderators", action="store_true",
                   help="run even if more moderators are listed than --max-moderators")
    a.add_argument("--correction", default="holm", choices=["holm", "bonferroni", "fdr_bh"])
    a.add_argument("--retest-sd-diff", type=float, default=None,
                   help="crossover: outside test-retest SD of the difference between two "
                   "measurements on the same untreated person")
    a.add_argument("--retest-sd-within", type=float, default=None,
                   help="crossover: outside within-person SD of one measurement "
                   "(converted to an SD of differences by multiplying by sqrt 2)")
    a.add_argument("--retest-df", type=float, default=None,
                   help="degrees of freedom of the outside estimate (people minus 1); "
                   "omit to treat it as known exactly")
    a.add_argument("--bootstrap", type=int, default=999)
    a.add_argument("--fpr-sims", type=int, default=400,
                   help="simulations for the heavy-tailed false-positive rate (0 = skip)")
    a.add_argument("--seed", type=int, default=0)
    a.add_argument("--json", action="store_true", help="print JSON instead of text")

    s = sub.add_parser("simulate", help="write a simulated trial with a known answer")
    s.add_argument("--design", choices=["parallel", "crossover"], required=True)
    s.add_argument("--n", type=int, required=True, help="total participants")
    s.add_argument("--responder-share", type=float, required=True)
    s.add_argument("--responder-effect", type=float, required=True)
    s.add_argument("--between-sd", type=float, required=True)
    s.add_argument("--noise-sd", type=float, required=True,
                   help="SD of one measurement around a person's true level")
    s.add_argument("--moderator-corr", type=float, default=0.0)
    s.add_argument("--baseline-mean", type=float, default=0.0)
    s.add_argument("--period-effect", type=float, default=0.0)
    s.add_argument("--carryover", type=float, default=0.0)
    s.add_argument("--noise", choices=NOISE_KINDS, default="normal")
    s.add_argument("--seed", type=int, default=0)
    s.add_argument("--out", default="-", help="output CSV path, '-' for stdout")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "simulate":
        sc = Scenario(
            design=args.design, n=args.n, responder_share=args.responder_share,
            responder_effect=args.responder_effect, between_sd=args.between_sd,
            noise_sd=args.noise_sd, moderator_corr=args.moderator_corr,
            baseline_mean=args.baseline_mean, period_effect=args.period_effect,
            carryover=args.carryover, noise=args.noise,
        )
        df = simulate_trial(sc, args.seed)
        df.to_csv(sys.stdout if args.out == "-" else args.out, index=False)
        return 0

    if args.retest_sd_diff is not None and args.retest_sd_within is not None:
        print("error: give --retest-sd-diff or --retest-sd-within, not both", file=sys.stderr)
        return 2
    retest = args.retest_sd_diff
    if args.retest_sd_within is not None:
        retest = args.retest_sd_within * 2**0.5
    try:
        result = analyze(
            pd.read_csv(args.csv, keep_default_na=True),
            moderators=args.moderators,
            design=args.design,
            treatment_label=args.treatment_label,
            retest_sd_difference=retest,
            retest_df=args.retest_df,
            max_moderators=args.max_moderators,
            allow_many_moderators=args.allow_many_moderators,
            correction=args.correction,
            n_bootstrap=args.bootstrap,
            seed=args.seed,
            fpr_sims=args.fpr_sims,
        )
    except (FormatError, TooManyModerators, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2) if args.json else format_report(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
