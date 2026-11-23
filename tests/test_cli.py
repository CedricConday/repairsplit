import json

import pandas as pd
import pytest

from repairsplit.analyze import FormatError, analyze
from repairsplit.cli import main
from repairsplit.simulate import Scenario, simulate_trial

FAST = ["--bootstrap", "99", "--fpr-sims", "0"]


def _sim(tmp_path, design, extra=()):
    out = tmp_path / f"{design}.csv"
    rc = main([
        "simulate", "--design", design, "--n", "60", "--responder-share", "0.5",
        "--responder-effect", "-8", "--between-sd", "11", "--noise-sd", "2.8",
        "--baseline-mean", "125", "--seed", "1", "--out", str(out), *extra,
    ])
    assert rc == 0
    return out


def test_parallel_round_trip(tmp_path, capsys):
    path = _sim(tmp_path, "parallel")
    df = pd.read_csv(path)
    assert len(df) == 60 and set(df["arm"]) == {"treatment", "control"}
    assert main(["analyze", str(path), "--moderators", "age", "baseline", "--json", *FAST]) == 0
    r = json.loads(capsys.readouterr().out)
    assert r["design"] == "parallel" and r["n"] == 60
    assert r["mean_effect"] == pytest.approx(-4.0, abs=3.0)
    assert len(r["moderators"]) == 2
    assert "Not medical advice" in r["disclaimer"]


def test_crossover_round_trip(tmp_path, capsys):
    path = _sim(tmp_path, "crossover", ["--period-effect", "1"])
    df = pd.read_csv(path)
    assert len(df) == 120 and set(df["sequence"]) == {"TC", "CT"}
    assert main(["analyze", str(path), *FAST]) == 0
    text = capsys.readouterr().out
    assert "cannot separate" in text and "Upper bound" in text
    assert main(["analyze", str(path), "--retest-sd-within", "2.8", "--retest-df", "38",
                 "--json", *FAST]) == 0
    r = json.loads(capsys.readouterr().out)
    assert r["crossover"]["sd_ir_estimable"]
    assert r["crossover"]["retest_sd_difference"] == pytest.approx(2.8 * 2**0.5)
    assert r["crossover"]["period_effect"] == pytest.approx(1.0, abs=1.5)


def test_too_many_moderators_is_refused(tmp_path, capsys):
    path = _sim(tmp_path, "parallel")
    df = pd.read_csv(path)
    for c in "xyz":
        df[c] = df["age"] * 1.0
    df.to_csv(path, index=False)
    args = ["analyze", str(path), "--moderators", "age", "baseline", "x", "y", *FAST]
    assert main(args) == 2
    assert "limit is 3" in capsys.readouterr().err
    assert main([*args, "--allow-many-moderators"]) == 0


def test_format_errors():
    df = simulate_trial(Scenario("crossover", 20, 0.5, -4, 3, 1), 0)
    with pytest.raises(FormatError, match="TC"):
        analyze(df.assign(sequence="AB"), n_bootstrap=19, fpr_sims=0)
    with pytest.raises(FormatError, match="period"):
        analyze(df.assign(period=3), n_bootstrap=19, fpr_sims=0)
    with pytest.raises(FormatError, match="missing"):
        analyze(df.drop(columns=["outcome"]), n_bootstrap=19, fpr_sims=0)
    with pytest.raises(FormatError, match="arm"):
        analyze(df.drop(columns=["sequence", "arm"]), n_bootstrap=19, fpr_sims=0)
