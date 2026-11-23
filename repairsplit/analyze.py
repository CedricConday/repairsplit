"""Read a tidy trial CSV and run every method that the design supports.

See docs/DATA_FORMAT.md for the layout.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .crossover import analyze_differences, period_adjusted_differences
from .mixture import mixture_check
from .moderators import DEFAULT_MAX_MODERATORS, check_count, moderators_crossover
from .moderators import moderators_parallel as _moderators_parallel
from .variance import brown_forsythe_p, sd_ir

DISCLAIMER = (
    "Statistical description of trial outcomes only. Not medical advice and not a "
    "statement about any individual participant."
)


class FormatError(ValueError):
    pass


def _has(df: pd.DataFrame, col: str) -> bool:
    if col not in df.columns:
        return False
    s = df[col]
    return bool((s.notna() & (s.astype(str).str.strip() != "")).any())


def detect_design(df: pd.DataFrame) -> str:
    if _has(df, "sequence"):
        return "crossover"
    if _has(df, "arm"):
        return "parallel"
    raise FormatError("need an 'arm' column (parallel) or a 'sequence' column (crossover)")


def _require(df, cols):
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise FormatError(f"missing column(s): {', '.join(missing)}")


def _covariates(frame, moderators):
    _require(frame, moderators)
    cov = frame[list(moderators)].apply(pd.to_numeric, errors="coerce")
    if cov.isna().any().any():
        raise FormatError("moderator columns must be numeric with no missing values")
    return cov


def analyze_parallel(
    df, moderators, treatment_label, max_moderators, allow_many, method, n_bootstrap, seed,
    fpr_sims,
) -> dict:
    _require(df, ["participant", "arm", "baseline", "outcome"])
    if df["participant"].duplicated().any():
        raise FormatError("parallel design: one row per participant expected")
    labels = sorted(df["arm"].astype(str).unique())
    if len(labels) != 2 or treatment_label not in labels:
        raise FormatError(
            f"'arm' must hold exactly two labels, one of them '{treatment_label}'; found {labels}"
        )
    df = df.dropna(subset=["baseline", "outcome"])
    treated = (df["arm"].astype(str) == treatment_label).to_numpy()
    change = (df["outcome"] - df["baseline"]).to_numpy(dtype=float)
    xt, xc = change[treated], change[~treated]
    res = sd_ir(xt, xc)
    t_bf, p_bf = brown_forsythe_p(xt, xc)
    out = {
        "design": "parallel",
        "n": int(change.size),
        "mean_effect": float(xt.mean() - xc.mean()),
        "sd_individual_response": res.to_dict(),
        "brown_forsythe": {"t": float(t_bf), "p_one_sided": float(p_bf)},
        "mixture": mixture_check(xt, n_bootstrap, seed=seed, fpr_sims=fpr_sims).to_dict(),
        "moderators": [],
    }
    if moderators:
        rows = _moderators_parallel(
            change, treated, _covariates(df, moderators), method=method,
            max_moderators=max_moderators, allow_many=allow_many,
        )
        out["moderators"] = [r.to_dict() for r in rows]
        out["moderator_correction"] = method
    return out


def crossover_wide(df: pd.DataFrame) -> pd.DataFrame:
    """One row per participant: sequence, treated and control outcome, difference."""
    _require(df, ["participant", "sequence", "period", "outcome"])
    df = df.copy()
    df["sequence"] = df["sequence"].astype(str).str.strip().str.upper()
    bad = sorted(set(df["sequence"]) - {"TC", "CT"})
    if bad:
        raise FormatError(f"'sequence' must be 'TC' or 'CT'; found {bad}")
    df["period"] = pd.to_numeric(df["period"], errors="coerce")
    if not set(df["period"].dropna().unique()) <= {1, 2}:
        raise FormatError("'period' must be 1 or 2; replicated periods are not supported")
    if df.duplicated(["participant", "period"]).any():
        raise FormatError("more than one row for a participant and period")
    if (df.groupby("participant")["sequence"].nunique() > 1).any():
        raise FormatError("a participant has two different sequences")
    wide = df.pivot(index="participant", columns="period", values="outcome").dropna()
    if wide.shape[1] != 2:
        raise FormatError("both periods are needed")
    first = df.drop_duplicates("participant").set_index("participant")
    wide = wide.join(first.drop(columns=["period", "outcome"]))
    wide["treatment_first"] = wide["sequence"] == "TC"
    wide["difference"] = np.where(wide["treatment_first"], wide[1] - wide[2], wide[2] - wide[1])
    return wide


def analyze_crossover(
    df, moderators, retest_sd_difference, retest_df, max_moderators, allow_many, method,
    n_bootstrap, seed, fpr_sims,
) -> dict:
    wide = crossover_wide(df)
    tf = wide["treatment_first"].to_numpy()
    d = wide["difference"].to_numpy(dtype=float)
    res = analyze_differences(d[tf], d[~tf], retest_sd_difference, retest_df)
    a_tc, a_ct = period_adjusted_differences(d[tf], d[~tf])
    out = {
        "design": "crossover",
        "n": int(d.size),
        "mean_effect": res.mean_effect,
        "crossover": res.to_dict(),
        "mixture": mixture_check(
            np.concatenate([a_tc, a_ct]), n_bootstrap, seed=seed, fpr_sims=fpr_sims
        ).to_dict(),
        "moderators": [],
    }
    if moderators:
        rows = moderators_crossover(
            d, tf, _covariates(wide, moderators), method=method,
            max_moderators=max_moderators, allow_many=allow_many,
        )
        out["moderators"] = [r.to_dict() for r in rows]
        out["moderator_correction"] = method
    return out


def analyze(
    df: pd.DataFrame,
    moderators: list[str] | None = None,
    design: str = "auto",
    treatment_label: str = "treatment",
    retest_sd_difference: float | None = None,
    retest_df: float | None = None,
    max_moderators: int = DEFAULT_MAX_MODERATORS,
    allow_many_moderators: bool = False,
    correction: str = "holm",
    n_bootstrap: int = 999,
    seed: int = 0,
    fpr_sims: int = 400,
) -> dict:
    moderators = list(moderators or [])
    check_count(moderators, max_moderators, allow_many_moderators)
    if design == "auto":
        design = detect_design(df)
    if design == "parallel":
        out = analyze_parallel(
            df, moderators, treatment_label, max_moderators, allow_many_moderators, correction,
            n_bootstrap, seed, fpr_sims,
        )
    elif design == "crossover":
        out = analyze_crossover(
            df, moderators, retest_sd_difference, retest_df, max_moderators,
            allow_many_moderators, correction, n_bootstrap, seed, fpr_sims,
        )
    else:
        raise FormatError(f"unknown design '{design}'")
    out["disclaimer"] = DISCLAIMER
    return out


def _f(x, nd=2):
    return "n/a" if x is None else f"{x:.{nd}f}"


def format_report(r: dict) -> str:
    """Plain-text report of an `analyze` result."""
    L = [f"Design: {r['design']}, {r['n']} participants analysed", ""]
    if r["design"] == "parallel":
        s = r["sd_individual_response"]
        L += [
            f"Mean effect (treated minus control change): {_f(r['mean_effect'])}",
            "",
            "Spread of change scores",
            f"  treated SD {_f(s['sd_treated'])} (n={s['n_treated']}), "
            f"control SD {_f(s['sd_control'])} (n={s['n_control']})",
            f"  SD of individual response: {_f(s['sd_ir'])} "
            f"(95% CI {_f(s['sd_ir_ci_low'])} to {_f(s['sd_ir_ci_high'])})",
            "  A negative value means the treated arm varied less than the control arm.",
            f"  variance ratio {_f(s['variance_ratio'])} "
            f"(95% CI {_f(s['variance_ratio_ci_low'])} to {_f(s['variance_ratio_ci_high'])})",
            f"  F test, treated more variable: one-sided p = {_f(s['p_f_one_sided'], 3)}",
            f"  Brown-Forsythe test, same question: one-sided p = "
            f"{_f(r['brown_forsythe']['p_one_sided'], 3)}",
        ]
    else:
        c = r["crossover"]
        L += [
            f"Mean effect (treated minus control): {_f(c['mean_effect'])} "
            f"(95% CI {_f(c['mean_effect_ci_low'])} to {_f(c['mean_effect_ci_high'])})",
            f"Period effect (period 2 minus period 1): {_f(c['period_effect'])}",
            "",
            "Individual response",
            f"  SD of within-person differences: {_f(c['sd_difference'])} (df={c['df']})",
            "  This is response spread and measurement noise added together.",
            f"  Upper bound on SD of individual response: {_f(c['sd_ir_upper_bound'])} "
            f"(95% upper confidence limit {_f(c['sd_ir_upper_bound_conf_limit'])})",
        ]
        if c["sd_ir_estimable"]:
            L += [
                f"  Outside test-retest SD of differences: {_f(c['retest_sd_difference'])} "
                f"(df={'treated as known' if c['retest_df'] is None else c['retest_df']})",
                f"  SD of individual response: {_f(c['sd_ir'])} "
                f"(95% CI {_f(c['sd_ir_ci_low'])} to {_f(c['sd_ir_ci_high'])})",
                f"  Test that differences vary more than noise: one-sided p = "
                f"{_f(c['p_response_variance'], 3)}",
            ]
        L += ["  " + c["statement"]]
    m = r["mixture"]
    L += [
        "",
        "Two-group mixture check (responders versus non-responders)",
        f"  likelihood-ratio statistic {_f(m['lrt'])}, bootstrap p = {_f(m['p_bootstrap'], 3)} "
        f"({m['n_bootstrap']} bootstrap samples, n={m['n']})",
        f"  best two-group fit: {_f(100 * m['weight_low'], 0)}% around {_f(m['mean_low'])}, "
        f"the rest around {_f(m['mean_high'])}, common SD {_f(m['component_sd'])}",
        f"  false-positive rate at this sample size: {_f(100 * m['false_positive_rate_normal'], 0)}"
        "% if noise is normal"
        + (
            ""
            if m["false_positive_rate_heavy_tailed"] is None
            else f", {_f(100 * m['false_positive_rate_heavy_tailed'], 0)}% if noise is "
            "heavy-tailed (t, 5 df)"
        ),
    ]
    if r["moderators"]:
        L += ["", f"Pre-specified moderators ({r['moderator_correction']} correction)"]
        for row in r["moderators"]:
            L.append(
                f"  {row['moderator']}: effect changes by {_f(row['interaction'], 3)} per unit "
                f"(95% CI {_f(row['ci_low'], 3)} to {_f(row['ci_high'], 3)}), "
                f"p = {_f(row['p_raw'], 3)}, corrected p = {_f(row['p_adjusted'], 3)}"
            )
    L += ["", r["disclaimer"]]
    return "\n".join(L)
