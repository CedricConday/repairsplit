# RepairSplit

Statistics for one question about small trials of myelin repair in multiple sclerosis.

Nothing here is medical advice. It describes trial statistics, not people, and it says nothing
about whether anyone should take any drug.

## The question

A trial reports that a drug shortened visual evoked potential latency by a millisecond or two on
average. Did some participants respond and others not? Or did everyone shift a little?

The average cannot tell. Both stories give the same average.

The trials are small, about 50 to 70 people. They measure a continuous outcome: mainly P100
latency in milliseconds, also MRI values per lesion. They are either two-arm parallel trials or
two-period crossovers.

No participant-level data from these trials is public. It is available on request only (see
`docs/DATA_ACCESS.md`). So this version contains:

1. the methods;
2. proof on simulated trials where the answer is known;
3. a statement of what each published trial design could and could not have detected.

It has not been run on real trial data.

## The headline

**Trials of this size cannot tell responders from a uniform shift at the effect sizes they
reported.**

Each row takes a published trial design and asks: suppose half the participants got twice the
reported mean effect and the other half got nothing. How often would each method notice? The
range is over the assumed noise level, which is not published (see below). The last column is
how often the same methods fire when everyone truly shifts by the same amount.

| Trial design | Reported mean effect | Variance test | Mixture check | False-positive rate |
|---|---|---|---|---|
| Clemastine crossover (ReBUILD), 50 people, trial data alone | 1.7 ms | **no test possible** | 5% | 5% to 6% |
| Same, with an outside test-retest noise estimate from 39 people | 1.7 ms | 7% to 14% | 5% | 5% to 6% |
| Same, noise known exactly (best case) | 1.7 ms | 10% to 23% | 5% | 5% to 6% |
| Bexarotene (CCMR One), 26 per arm, lesional MTR | 0.16 pu | 5% to 6% | 4% | 4% to 5% |
| Bexarotene (CCMR One), 28 people with delayed VEP | 4.06 ms | 12% to 36% | 6% to 7% | 4% to 6% |
| Metformin plus clemastine (CCMR Two), 33 and 34 | 1.2 ms | 5% to 16% | 5% to 6% | 4% to 6% |

A power of 5% is the same as the false-positive rate. It means the method sees nothing.

To reach 80% power on a half split, responders would have to improve by 2 to 3.5 times the SD of
a change score. At an SD of 5 ms that is 10 to 17.5 ms in the responders. The reported mean
effects are 1.2 to 4.1 ms.

In plain words: these trials were built to detect an average effect, and some did. They were not
built to say who responded, and they cannot. A statement such as "about half of patients
respond" does not follow from trials like these. Neither does "everyone responds a little". The
data cannot separate the two.

Full tables, inputs and commands: `docs/VALIDATION.md`.

## Generic power, known-answer test

Simulated trials with half the participants responding. Effect sizes are in SDs of a change
score. 2000 trials per cell.

| Design, n=60 | Method | Responder effect 1 SD | 2 SD | 3 SD | False-positive rate |
|---|---|---|---|---|---|
| Parallel | Variance-ratio F test | 15% | 60% | 97% | 5% |
| Parallel | Brown-Forsythe test | 13% | 60% | 97% | 4% to 5% |
| Parallel | Mixture check | 5% | 8% | 37% | 4% |
| Parallel | Moderators, if responders follow age (r=0.7) | 12% | 32% | 54% | 4% to 5% |
| Crossover | Trial data alone | none | none | none | not applicable |
| Crossover | Outside noise from 39 people | 17% | 76% | 99% | 5% to 6% |
| Crossover | Outside noise known exactly | 34% | 99% | 100% | 6% |
| Crossover | Mixture check | 5% | 14% | 62% | 4% to 5% |
| Crossover | Moderators, if responders follow age (r=0.7) | 38% | 85% | 96% | 5% |

With heavy-tailed noise and no responders at all, the false-positive rate rises to about 10% for
the F test, 9% to 12% for the known-noise crossover test, and 7% to 76% for the mixture check
(worse in larger trials). The Brown-Forsythe test and the moderator analysis stay near 5%.

## The methods

**SD of individual response (parallel trials).** Nobody in a parallel trial is seen on both
treatments, so no individual response is ever observed. What is observed is how spread out the
changes are in each arm. If treatment adds a response that differs between people, the treated
arm is more spread out. The variance of individual response is the treated-arm variance of
change minus the control-arm variance. The tool reports its square root with a confidence
interval, the variance ratio, an F test and a Brown-Forsythe test. A negative value is reported
as negative: it means the treated arm varied less.

**Crossover trials.** Each person gives one value on treatment and one on control. The spread of
their differences is response spread plus measurement noise, added together. A plain two-period
crossover cannot separate them. A person who "did better on the drug" may have had two noisy
measurements. The tool reports what is estimable: the mean effect, the period effect, and an
upper bound on the SD of individual response. If you supply an outside test-retest noise value,
it subtracts that and reports an estimate, an interval and a test. That estimate is only as good
as the outside value. Replicated crossovers, which solve this properly, are not supported yet.

**Moderator analysis.** For each covariate named in advance (for example age, baseline latency),
one linear treatment-by-covariate interaction. P-values are corrected for the number of
moderators (Holm by default). More than three moderators are refused unless you pass
`--allow-many-moderators`. A moderator can only find responders who differ on something you
measured and named beforehand.

**Mixture check.** Fits one normal distribution and a mixture of two to the treated-arm changes
(or crossover differences), and compares them with a bootstrap likelihood-ratio test. The output
states the test's false-positive rate: 5% if the noise is normal, and a simulated rate at your
sample size if the noise is heavy-tailed. This is the weakest and most fragile method here. It is
included because fitting "responder" clusters is common, and its error rates should be seen.

## Use

```
pip install repairsplit

# a simulated trial with a known answer
repairsplit simulate --design parallel --n 60 --responder-share 0.5 --responder-effect -8 \
    --between-sd 11 --noise-sd 2.8 --baseline-mean 125 --seed 1 --out trial.csv

repairsplit analyze trial.csv --moderators age baseline

# crossover, with an outside test-retest SD of differences
repairsplit analyze crossover.csv --retest-sd-diff 3.85 --retest-df 38
```

Input is one tidy CSV: `participant`, `arm` or `sequence`, `period`, `baseline`, `outcome`, and
any covariates. See `docs/DATA_FORMAT.md`. Add `--json` for machine-readable
output.

## Which inputs were assumptions

Every trial number was read from a source fetched on 2026-11-23 and is listed with its source in
`docs/VALIDATION.md`. These were not published and were assumed, with a sweep:

- The noise level: the SD of a change score, or of a within-person difference, per participant.
  Swept from 3.85 ms to 6.5 ms, the lowest and highest published test-retest SDs for P100
  latency, with the 5 ms planning value of the CCMR Two protocol in between. For CCMR Two also
  2.4 ms, a lower limit derived from its reported confidence interval. The MTR noise level was
  published and needed no sweep.
- That each participant gives one independent value. The trials analysed eyes or lesions.
- The number analysed per arm in CCMR One (26 assumed) and the split of its 28 VEP participants
  (14 and 14 assumed).
- No carryover in the crossover, although the trial itself reported a lasting effect.
- For the moderator rows, that responder status follows a named covariate with r = 0.7.

The CCMR Two result is known only from conference reports. No results paper was found.

## What this does not show

- It does not show that there are no responders. It shows these designs could not have seen them.
- It does not show that everyone responds the same. Same reason.
- It does not analyse any real participant. All power figures are simulations.
- It does not say anything about any drug's benefit, safety or mechanism.
- The simulated truth is two clean groups with equal, normal noise. Real data will be messier:
  graded responses, clustered eyes, dropout, carryover, noise that differs between arms. All of
  these make detection harder or the tests less trustworthy, not easier.
- A larger variance in the treated arm is not proof of responders. Treatment can change
  measurement noise, and floor or ceiling effects change spread.
- One published summary does hint at unequal spread: the ReBUILD registry entry reports an SD of
  change of 6.85 ms in clemastine periods and 3.86 ms in placebo periods, per eye. No valid test
  can be run on those two numbers (same people, two eyes each, unequal periods, carryover). Only
  the participant-level data could say what it means.

## Tests

```
ruff check .
pytest -q
```

The test suite includes small known-answer runs: false-positive rates near 5%, high power for a
large split in a large trial, low power for a small split in a small trial.

## Credits for the methods

Each of these was looked up on 2026-11-23. For papers behind a paywall only the abstract or the
bibliographic record was read.

- SD of individual response from the difference in change-score variances: Atkinson G, Batterham
  AM. True and false interindividual differences in the physiological response to an
  intervention. Exp Physiol 2015;100:577-588. doi:10.1113/EP085070. Hopkins WG. Individual
  responses made easy. J Appl Physiol 2015;118:1444-1446. doi:10.1152/japplphysiol.00098.2015.
- Why crossovers confound individual response with noise, and variance components generally:
  Senn S. Individual therapy: new dawn or false dawn? Drug Inf J 2001;35:1479-1494.
  doi:10.1177/009286150103500443. Senn S. Mastering variation: variance components and
  personalised medicine. Stat Med 2016;35:966-977. doi:10.1002/sim.6739.
- Comparing variances between trial arms to detect varying effects: Mills HL et al. Detecting
  heterogeneity of intervention effects using analysis and meta-analysis of differences in
  variance between trial arms. Epidemiology 2021;32:846-854. doi:10.1097/EDE.0000000000001401.
  Winkelbeiner S et al. Evaluation of differences in individual treatment response in
  schizophrenia spectrum disorders. JAMA Psychiatry 2019;76:1063-1073.
  doi:10.1001/jamapsychiatry.2019.1530.
- Robust test for equal variances: Brown MB, Forsythe AB. Robust tests for the equality of
  variances. J Am Stat Assoc 1974;69:364-367. doi:10.1080/01621459.1974.10482955.
- Bootstrap likelihood-ratio test for the number of mixture components: McLachlan GJ. On
  bootstrapping the likelihood ratio test statistic for the number of components in a normal
  mixture. Appl Stat 1987;36(3):318. doi:10.2307/2347790.
- Multiplicity correction: Holm S. A simple sequentially rejective multiple test procedure.
  Scand J Stat 1979;6:65-70. JSTOR 4615733.

Trial sources are cited in `docs/VALIDATION.md`. Article metadata and
abstracts came from PubMed; open full texts came from PubMed Central.

## Licence

MIT. Copyright (c) 2026 Cedric Conday.
