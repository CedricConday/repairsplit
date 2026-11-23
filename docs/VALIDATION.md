# Validation

Everything here is simulation. No participant-level trial data was used. Nothing here is medical
advice.

Run on 2026-11-23 with Python 3.12, numpy 2.5.5, scipy 1.18.1, pandas 3.1.1, statsmodels 0.15.0.
All runs are seeded; the same commands give the same tables.

## Commands

```
python -m venv ~/.venvs/repairsplit
~/.venvs/repairsplit/bin/pip install -e ".[dev]"
ruff check .
pytest -q
python scripts/known_answer.py --out results/known_answer.csv      # 120 cells x 2000 trials
python scripts/trial_designs.py --out results/trial_designs.csv    # 4000 trials per cell
python scripts/make_tables.py > results/tables.md
```

Result files:

- `results/known_answer.csv`: one row per design, sample size and truth.
- `results/trial_designs.csv`: one row per trial design, effect, SD and split.
- `results/trial_detectable_effect.csv`: responder effect needed for 80% power.
- `results/summary_statistic_checks.json`: the two checks on published SDs.
- `results/tables.md`: the tables below, generated from the CSVs.

## How to read the numbers

- A "rejection" is a test at the 5% level concluding that participants differ in their response.
- When the truth is "nobody responds" or "everybody responds the same", the rejection rate is the
  **false-positive rate**. It should be 5%.
- When the truth has responders and non-responders, the rejection rate is the **power**.
- Each rate comes from 2000 simulated trials (4000 for the trial designs). The Monte Carlo
  standard error is about 0.5 percentage points near 5% and about 1 point near 50%.
- Variance tests are one-sided: does treatment add spread?
- Sample size n is the whole trial. A parallel trial has n/2 per arm. The mixture check in a
  parallel trial sees only the treated arm, so n/2 values.

## Known-answer set-up

Units are standardised. One measurement has noise SD 1. A change score, or a crossover
difference, therefore has noise SD 1.41 ("1 SD of change"). People differ in their true level with
SD 3. Responder effects are 1, 2 or 3 SDs of change. Responder shares are 0%, 25%, 50% and 100%.
Sample sizes are 30, 60, 100, 200 and 500.

For the crossover, the outside noise estimate is drawn fresh for every simulated trial as a
variance estimate from 39 people (38 degrees of freedom, the size of the largest VEP test-retest
study found; see inputs below), or taken as known exactly. A plain two-period crossover with no
outside noise estimate has no test of response spread at all, so it has no row. Its power for this
question is zero by construction, not by simulation.

For the moderator rows, two moderators are pre-specified (age and baseline) and Holm-corrected. A
rejection means at least one is significant after correction. In the power rows responder status
is tied to age with correlation 0.7 on the latent scale, a favourable case.

The mixture check in the simulations compares the statistic with a critical value from 4000 null
samples of the same size, instead of bootstrapping inside every simulated trial. This is the
bootstrap test with many bootstrap samples, because the statistic does not depend on location or
scale under the normal null. A unit test checks that the two agree.

## Known-answer results

Copied from `results/tables.md`.

### Parallel design: false-positive rate (nominal 5%)

| Method | Truth | n=30 | n=60 | n=100 | n=200 | n=500 |
|---|---|---|---|---|---|---|
| Variance-ratio F test | nobody responds | 5% | 5% | 5% | 5% | 4% |
| Variance-ratio F test | everybody responds the same | 4% | 5% | 4% | 6% | 6% |
| Variance-ratio F test | same, heavy-tailed noise | 10% | 10% | 10% | 12% | 11% |
| Brown-Forsythe test | nobody responds | 4% | 4% | 5% | 5% | 4% |
| Brown-Forsythe test | everybody responds the same | 3% | 5% | 4% | 6% | 5% |
| Brown-Forsythe test | same, heavy-tailed noise | 5% | 4% | 5% | 5% | 4% |
| Mixture bootstrap LRT | nobody responds | 4% | 4% | 5% | 6% | 4% |
| Mixture bootstrap LRT | everybody responds the same | 4% | 4% | 6% | 5% | 4% |
| Mixture bootstrap LRT | same, heavy-tailed noise | 7% | 13% | 19% | 30% | 54% |
| Two moderators, Holm | nobody responds | 5% | 4% | 5% | 5% | 5% |
| Two moderators, Holm | everybody responds the same | 5% | 5% | 5% | 5% | 6% |
| Two moderators, Holm | same, heavy-tailed noise | 5% | 6% | 6% | 6% | 6% |
| Two moderators, Holm | responders exist, unrelated to covariates | 5% | 5% | 5% | 5% | 5% |

### Parallel design: power to detect responders

| Method | Responder share | Responder effect | True SD of response | n=30 | n=60 | n=100 | n=200 | n=500 |
|---|---|---|---|---|---|---|---|---|
| Variance-ratio F test | 25% | 1 SD | 0.43 SD | 9% | 12% | 14% | 21% | 39% |
| Variance-ratio F test | 25% | 2 SD | 0.87 SD | 27% | 44% | 62% | 88% | 100% |
| Variance-ratio F test | 25% | 3 SD | 1.30 SD | 58% | 86% | 97% | 100% | 100% |
| Variance-ratio F test | 50% | 1 SD | 0.50 SD | 12% | 15% | 17% | 29% | 55% |
| Variance-ratio F test | 50% | 2 SD | 1.00 SD | 33% | 60% | 79% | 98% | 100% |
| Variance-ratio F test | 50% | 3 SD | 1.50 SD | 73% | 96% | 100% | 100% | 100% |
| Brown-Forsythe test | 25% | 1 SD | 0.43 SD | 6% | 10% | 13% | 19% | 35% |
| Brown-Forsythe test | 25% | 2 SD | 0.87 SD | 20% | 36% | 55% | 82% | 99% |
| Brown-Forsythe test | 25% | 3 SD | 1.30 SD | 40% | 71% | 89% | 100% | 100% |
| Brown-Forsythe test | 50% | 1 SD | 0.50 SD | 9% | 13% | 16% | 28% | 52% |
| Brown-Forsythe test | 50% | 2 SD | 1.00 SD | 30% | 60% | 80% | 99% | 100% |
| Brown-Forsythe test | 50% | 3 SD | 1.50 SD | 70% | 97% | 100% | 100% | 100% |
| Mixture bootstrap LRT | 25% | 1 SD | 0.43 SD | 5% | 5% | 6% | 6% | 7% |
| Mixture bootstrap LRT | 25% | 2 SD | 0.87 SD | 6% | 9% | 15% | 29% | 65% |
| Mixture bootstrap LRT | 25% | 3 SD | 1.30 SD | 17% | 40% | 64% | 93% | 100% |
| Mixture bootstrap LRT | 50% | 1 SD | 0.50 SD | 4% | 5% | 5% | 5% | 6% |
| Mixture bootstrap LRT | 50% | 2 SD | 1.00 SD | 7% | 8% | 12% | 21% | 50% |
| Mixture bootstrap LRT | 50% | 3 SD | 1.50 SD | 17% | 37% | 61% | 92% | 100% |
| Two moderators, Holm (responders tied to age, r=0.7) | 50% | 1 SD | 0.50 SD | 8% | 12% | 19% | 35% | 79% |
| Two moderators, Holm (responders tied to age, r=0.7) | 50% | 2 SD | 1.00 SD | 17% | 32% | 56% | 89% | 100% |
| Two moderators, Holm (responders tied to age, r=0.7) | 50% | 3 SD | 1.50 SD | 25% | 54% | 80% | 99% | 100% |

### Crossover design: false-positive rate (nominal 5%)

| Method | Truth | n=30 | n=60 | n=100 | n=200 | n=500 |
|---|---|---|---|---|---|---|
| Outside noise, estimated from 39 people | nobody responds | 5% | 5% | 5% | 5% | 6% |
| Outside noise, estimated from 39 people | everybody responds the same | 5% | 6% | 5% | 5% | 4% |
| Outside noise, estimated from 39 people | same, heavy-tailed noise | 7% | 7% | 6% | 7% | 5% |
| Outside noise, known exactly | nobody responds | 5% | 6% | 5% | 4% | 5% |
| Outside noise, known exactly | everybody responds the same | 5% | 6% | 5% | 5% | 5% |
| Outside noise, known exactly | same, heavy-tailed noise | 9% | 9% | 11% | 11% | 12% |
| Mixture bootstrap LRT | nobody responds | 5% | 4% | 5% | 4% | 5% |
| Mixture bootstrap LRT | everybody responds the same | 4% | 5% | 5% | 4% | 5% |
| Mixture bootstrap LRT | same, heavy-tailed noise | 10% | 20% | 29% | 46% | 76% |
| Two moderators, Holm | nobody responds | 5% | 5% | 4% | 4% | 5% |
| Two moderators, Holm | everybody responds the same | 4% | 5% | 5% | 5% | 6% |
| Two moderators, Holm | same, heavy-tailed noise | 5% | 4% | 6% | 5% | 4% |
| Two moderators, Holm | responders exist, unrelated to covariates | 5% | 5% | 5% | 5% | 5% |

### Crossover design: power to detect responders

| Method | Responder share | Responder effect | True SD of response | n=30 | n=60 | n=100 | n=200 | n=500 |
|---|---|---|---|---|---|---|---|---|
| Outside noise, estimated from 39 people | 25% | 1 SD | 0.43 SD | 13% | 14% | 15% | 17% | 16% |
| Outside noise, estimated from 39 people | 25% | 2 SD | 0.87 SD | 48% | 60% | 65% | 68% | 74% |
| Outside noise, estimated from 39 people | 25% | 3 SD | 1.30 SD | 86% | 95% | 98% | 99% | 99% |
| Outside noise, estimated from 39 people | 50% | 1 SD | 0.50 SD | 15% | 17% | 19% | 21% | 20% |
| Outside noise, estimated from 39 people | 50% | 2 SD | 1.00 SD | 65% | 76% | 82% | 86% | 87% |
| Outside noise, estimated from 39 people | 50% | 3 SD | 1.50 SD | 97% | 99% | 100% | 100% | 100% |
| Outside noise, known exactly | 25% | 1 SD | 0.43 SD | 17% | 25% | 37% | 53% | 86% |
| Outside noise, known exactly | 25% | 2 SD | 0.87 SD | 71% | 93% | 99% | 100% | 100% |
| Outside noise, known exactly | 25% | 3 SD | 1.30 SD | 98% | 100% | 100% | 100% | 100% |
| Outside noise, known exactly | 50% | 1 SD | 0.50 SD | 22% | 34% | 49% | 73% | 97% |
| Outside noise, known exactly | 50% | 2 SD | 1.00 SD | 89% | 99% | 100% | 100% | 100% |
| Outside noise, known exactly | 50% | 3 SD | 1.50 SD | 100% | 100% | 100% | 100% | 100% |
| Mixture bootstrap LRT | 25% | 1 SD | 0.43 SD | 5% | 5% | 6% | 7% | 8% |
| Mixture bootstrap LRT | 25% | 2 SD | 0.87 SD | 8% | 16% | 29% | 55% | 93% |
| Mixture bootstrap LRT | 25% | 3 SD | 1.30 SD | 30% | 69% | 93% | 100% | 100% |
| Mixture bootstrap LRT | 50% | 1 SD | 0.50 SD | 5% | 5% | 6% | 5% | 6% |
| Mixture bootstrap LRT | 50% | 2 SD | 1.00 SD | 8% | 14% | 23% | 39% | 83% |
| Mixture bootstrap LRT | 50% | 3 SD | 1.50 SD | 29% | 62% | 90% | 100% | 100% |
| Two moderators, Holm (responders tied to age, r=0.7) | 50% | 1 SD | 0.50 SD | 18% | 38% | 61% | 93% | 100% |
| Two moderators, Holm (responders tied to age, r=0.7) | 50% | 2 SD | 1.00 SD | 48% | 84% | 98% | 100% | 100% |
| Two moderators, Holm (responders tied to age, r=0.7) | 50% | 3 SD | 1.50 SD | 68% | 96% | 100% | 100% | 100% |

### Parallel design: SD of individual response, interval coverage and bias

Each cell: coverage of the 95% interval / mean estimated variance difference. Variances are in squared measurement-noise units.

| Responder share | Responder effect | True variance difference | n=30 | n=60 | n=100 | n=200 | n=500 |
|---|---|---|---|---|---|---|---|
| 25% | 1 SD | 0.38 | 98% / 0.34 | 97% / 0.37 | 96% / 0.36 | 96% / 0.38 | 96% / 0.39 |
| 25% | 2 SD | 1.50 | 95% / 1.51 | 96% / 1.50 | 96% / 1.49 | 96% / 1.50 | 95% / 1.49 |
| 25% | 3 SD | 3.38 | 92% / 3.35 | 95% / 3.41 | 95% / 3.38 | 96% / 3.36 | 95% / 3.38 |
| 50% | 1 SD | 0.50 | 98% / 0.49 | 97% / 0.52 | 96% / 0.50 | 96% / 0.50 | 96% / 0.50 |
| 50% | 2 SD | 2.00 | 96% / 1.97 | 97% / 2.04 | 97% / 1.99 | 98% / 2.01 | 97% / 2.01 |
| 50% | 3 SD | 4.50 | 96% / 4.44 | 98% / 4.49 | 99% / 4.53 | 98% / 4.48 | 99% / 4.50 |
| 0% | 0 SD | 0.00 | 99% / 0.01 | 98% / 0.00 | 96% / -0.03 | 96% / 0.01 | 96% / -0.01 |
| 100% | 2 SD | 0.00 | 99% / -0.01 | 97% / -0.02 | 97% / 0.00 | 95% / 0.01 | 94% / 0.00 |

## What the known-answer tables show

1. **False-positive rates hold when the noise is normal.** Every method rejects in 3% to 6% of
   trials when nobody responds or everybody responds the same.
2. **Heavy-tailed noise breaks three of the methods.** With t-distributed noise (5 degrees of
   freedom) and no individual differences, the F test rejects in about 10% of trials, the
   known-noise crossover test in 9% to 12%, and the mixture check in 7% to 76%, getting worse
   as the trial gets larger. The Brown-Forsythe test and the moderator analysis stay near 5%.
   The interval for the SD of individual response covers the truth 84% to 91% of the time
   instead of 95% once n is 60 or more.
3. **Power in a parallel trial of 60 is low unless responders differ a lot.** With half the
   participants responding, the variance tests reach 13% to 15% power for a responder effect of
   1 SD of change, about 60% for 2 SD and 97% for 3 SD.
4. **The mixture check needs a very large gap.** At n=60 it has 5% to 8% power for 1 or 2 SD
   and 37% for 3 SD in a parallel trial. It is the weakest method in every cell.
5. **A crossover with an outside noise estimate is limited by that estimate, not by trial
   size.** With noise estimated from 39 people, power for a 2 SD half split is 65% at n=30 and
   only 87% at n=500. With the noise known exactly it is 89% at n=30. A larger crossover does
   not help much; a larger test-retest study would.
6. **Moderators only help if the moderator is real and measured.** When responders are a random
   subset the moderator analysis rejects 5% of the time, as it should. When responder status is
   tied to age (r=0.7), power at n=60 is 12% to 54% in a parallel trial and 38% to 96% in a
   crossover.

## Inputs for the trial designs

Every number was read from a source fetched on 2026-11-23. The machine-readable version, with the
exact wording of each source note, is `scripts/trial_inputs.json`. "Assumption" means the number
is not published in any source that could be reached.

| Trial | Quantity | Value | Status | Source |
|---|---|---|---|---|
| ReBUILD | Design, size | Two-period crossover, 50 randomised, 25 per sequence, all completed; periods of 90 and 60 days | Published | PMID 29029896, abstract |
| ReBUILD | Mean effect, crossover analysis | 1.7 ms per eye shorter P100 latency (95% CI 0.5 to 2.9) | Published | PMID 29029896, abstract |
| ReBUILD | Mean effect, delayed-treatment analysis | 3.2 ms | Published, second-hand | Quoted in the CCMR Two protocol, PMID 41361285 |
| ReBUILD | Baseline latency, mean (SD), per eye | 124.8 (11.5) and 126.4 (10.9) ms | Published | NCT02040298 results |
| ReBUILD | Change from baseline, mean (SD), per eye, 93 eyes | clemastine periods -2.86 (6.85) ms; placebo periods -1.50 (3.86) ms | Published | NCT02040298 results |
| ReBUILD | SD of within-person treated-minus-control difference, per participant | 3.85, 5.0, 6.5 ms | **Assumption**, swept | Range of published test-retest SDs below |
| CCMR One | Design, size | Parallel, 52 randomised, 26 per arm | Published | PMID 34418398, abstract |
| CCMR One | Number analysed per arm | 26 | **Assumption** (upper limit) | The abstract gives only the number randomised |
| CCMR One | Primary outcome: lesional MTR change, mean (SD) | bexarotene 0.25 (0.98) pu; placebo 0.09 (0.84) pu; adjusted difference 0.16 pu (95% CI -0.39 to 0.71) | Published | PMID 34418398, abstract |
| CCMR One | VEP effect, eyes with baseline latency above 118 ms | -4.06 ms | Published, second-hand, no CI | PMID 38426437, full text |
| CCMR One | Participants with such eyes | 28 (51 eyes) | Published | PMID 40008332, full text |
| CCMR One | Split of those 28 between arms | 14 and 14 | **Assumption** | Not given |
| CCMR One | SD of VEP change | 3.85, 5.0, 6.5 ms | **Assumption**, swept | Not found in any source reached |
| CCMR Two | Design, size | Parallel, 70 randomised (34 and 36), 33 and 34 completed | Published, conference reports only | ECTRIMS 2025 abstract 152/O133 as reported |
| CCMR Two | Mean effect | -1.2 ms (95% CI -2.4 to -0.1), p=0.042 | Published, conference reports only | Same |
| CCMR Two | Planned SD of VEP change, target effect | 5 ms, 3 ms; the protocol says the ReBUILD SD was about 4.1 ms | Published | PMID 41361285, full text |
| CCMR Two | SD of VEP change in the trial | 2.4, 3.85, 5.0, 6.5 ms | **Assumption**, swept | Not reported. 2.4 ms is derived from the reported CI as a lower limit |
| VEP noise | Test-retest SD of P100 difference, about 2 days apart, 75 eyes of 39 patients, after blinded verification | 3.85 ms (8.02 ms before verification, 77 eyes) | Published | PMID 20634712, abstract |
| VEP noise | SD of P100 difference, one week apart, per eye, 15 people | 6.5 ms and 6.3 ms (two check sizes) | Published | PMID 32120028, abstract |
| VEP noise | Size of the outside noise study in the simulations | 39 people, 38 degrees of freedom | Derived | PMID 20634712 |
| Moderators | How strongly responder status follows a covariate | r = 0.7 | **Assumption**, favourable | Nothing published |
| All | One value per participant, independent participants | | **Assumption** | The trials analysed eyes or lesions within people |
| ReBUILD | No carryover, same noise in both periods | | **Assumption** | The trial reported a sustained effect after switching to placebo, so this is known to be imperfect |

Not used because not published: test-retest noise of lesional MTR for the CCMR One pipeline, and any
correlation between a participant's two eyes.

For each trial design and each SD, three truths with the same mean effect were simulated:
everyone shifts by the mean effect; half respond with twice the mean effect; a quarter respond
with four times the mean effect.

## Trial design results

Copied from `results/tables.md`. "SD of change" is the SD of a change score (parallel) or of a within-person difference (crossover) when nobody differs in response.

### ReBUILD (clemastine): crossover, n=50

| Mean effect | SD of change | Split | Effect in responders | True SD of response | Outside noise, estimated from 39 people | Outside noise, known exactly | Mixture bootstrap LRT | Moderators, responders random | Moderators, responders tied (r=0.7) |
|---|---|---|---|---|---|---|---|---|---|
| -1.7 (crossover estimate) | 3.85 | uniform | -1.7 | 0.00 | 5% | 5% | 5% | 5% | 5% |
| -1.7 (crossover estimate) | 3.85 | half | -3.4 | 1.70 | 14% | 23% | 5% | 5% | 26% |
| -1.7 (crossover estimate) | 3.85 | quarter | -6.8 | 2.94 | 44% | 75% | 11% | 5% | 50% |
| -1.7 (crossover estimate) | 5 | uniform | -1.7 | 0.00 | 5% | 5% | 5% | 5% | 5% |
| -1.7 (crossover estimate) | 5 | half | -3.4 | 1.70 | 11% | 14% | 5% | 5% | 18% |
| -1.7 (crossover estimate) | 5 | quarter | -6.8 | 2.94 | 23% | 45% | 6% | 5% | 34% |
| -1.7 (crossover estimate) | 6.5 | uniform | -1.7 | 0.00 | 5% | 5% | 6% | 5% | 4% |
| -1.7 (crossover estimate) | 6.5 | half | -3.4 | 1.70 | 7% | 10% | 5% | 5% | 12% |
| -1.7 (crossover estimate) | 6.5 | quarter | -6.8 | 2.94 | 15% | 25% | 4% | 5% | 24% |
| -3.2 (delayed-treatment estimate) | 3.85 | uniform | -3.2 | 0.00 | 5% | 5% | 5% | 4% | 5% |
| -3.2 (delayed-treatment estimate) | 3.85 | half | -6.4 | 3.20 | 51% | 86% | 7% | 5% | 64% |
| -3.2 (delayed-treatment estimate) | 3.85 | quarter | -12.8 | 5.54 | 98% | 100% | 77% | 5% | 82% |
| -3.2 (delayed-treatment estimate) | 5 | uniform | -3.2 | 0.00 | 5% | 5% | 6% | 5% | 5% |
| -3.2 (delayed-treatment estimate) | 5 | half | -6.4 | 3.20 | 30% | 56% | 5% | 4% | 47% |
| -3.2 (delayed-treatment estimate) | 5 | quarter | -12.8 | 5.54 | 83% | 99% | 34% | 5% | 71% |
| -3.2 (delayed-treatment estimate) | 6.5 | uniform | -3.2 | 0.00 | 5% | 6% | 5% | 5% | 5% |
| -3.2 (delayed-treatment estimate) | 6.5 | half | -6.4 | 3.20 | 17% | 30% | 5% | 5% | 30% |
| -3.2 (delayed-treatment estimate) | 6.5 | quarter | -12.8 | 5.54 | 54% | 85% | 13% | 5% | 57% |

### CCMR One (bexarotene), lesional MTR: parallel, n=52

| Mean effect | SD of change | Split | Effect in responders | True SD of response | Variance-ratio F test | Brown-Forsythe test | Mixture bootstrap LRT | Moderators, responders random | Moderators, responders tied (r=0.7) |
|---|---|---|---|---|---|---|---|---|---|
| 0.16 (adjusted difference) | 0.84 | uniform | 0.16 | 0.00 | 5% | 4% | 5% | 5% | 5% |
| 0.16 (adjusted difference) | 0.84 | half | 0.32 | 0.16 | 6% | 5% | 4% | 5% | 6% |
| 0.16 (adjusted difference) | 0.84 | quarter | 0.64 | 0.28 | 7% | 7% | 6% | 5% | 8% |

### CCMR One (bexarotene), VEP: parallel, n=28

| Mean effect | SD of change | Split | Effect in responders | True SD of response | Variance-ratio F test | Brown-Forsythe test | Mixture bootstrap LRT | Moderators, responders random | Moderators, responders tied (r=0.7) |
|---|---|---|---|---|---|---|---|---|---|
| -4.06 (eyes with baseline above 118 ms) | 3.85 | uniform | -4.06 | 0.00 | 5% | 4% | 6% | 5% | 5% |
| -4.06 (eyes with baseline above 118 ms) | 3.85 | half | -8.12 | 4.06 | 36% | 33% | 7% | 5% | 15% |
| -4.06 (eyes with baseline above 118 ms) | 3.85 | quarter | -16.24 | 7.03 | 83% | 55% | 55% | 6% | 24% |
| -4.06 (eyes with baseline above 118 ms) | 5 | uniform | -4.06 | 0.00 | 4% | 4% | 5% | 5% | 5% |
| -4.06 (eyes with baseline above 118 ms) | 5 | half | -8.12 | 4.06 | 21% | 19% | 6% | 5% | 12% |
| -4.06 (eyes with baseline above 118 ms) | 5 | quarter | -16.24 | 7.03 | 62% | 44% | 24% | 5% | 19% |
| -4.06 (eyes with baseline above 118 ms) | 6.5 | uniform | -4.06 | 0.00 | 5% | 4% | 5% | 5% | 5% |
| -4.06 (eyes with baseline above 118 ms) | 6.5 | half | -8.12 | 4.06 | 14% | 12% | 6% | 5% | 9% |
| -4.06 (eyes with baseline above 118 ms) | 6.5 | quarter | -16.24 | 7.03 | 39% | 29% | 11% | 5% | 15% |

### CCMR Two (metformin + clemastine): parallel, n=67

| Mean effect | SD of change | Split | Effect in responders | True SD of response | Variance-ratio F test | Brown-Forsythe test | Mixture bootstrap LRT | Moderators, responders random | Moderators, responders tied (r=0.7) |
|---|---|---|---|---|---|---|---|---|---|
| -1.2 (adjusted difference) | 2.4 | uniform | -1.2 | 0.00 | 5% | 5% | 6% | 5% | 5% |
| -1.2 (adjusted difference) | 2.4 | half | -2.4 | 1.20 | 16% | 13% | 6% | 5% | 13% |
| -1.2 (adjusted difference) | 2.4 | quarter | -4.8 | 2.08 | 45% | 38% | 12% | 5% | 26% |
| -1.2 (adjusted difference) | 3.85 | uniform | -1.2 | 0.00 | 5% | 4% | 5% | 5% | 5% |
| -1.2 (adjusted difference) | 3.85 | half | -2.4 | 1.20 | 8% | 7% | 5% | 5% | 8% |
| -1.2 (adjusted difference) | 3.85 | quarter | -4.8 | 2.08 | 17% | 15% | 6% | 5% | 14% |
| -1.2 (adjusted difference) | 5 | uniform | -1.2 | 0.00 | 5% | 4% | 5% | 5% | 5% |
| -1.2 (adjusted difference) | 5 | half | -2.4 | 1.20 | 7% | 6% | 5% | 5% | 7% |
| -1.2 (adjusted difference) | 5 | quarter | -4.8 | 2.08 | 11% | 10% | 6% | 5% | 10% |
| -1.2 (adjusted difference) | 6.5 | uniform | -1.2 | 0.00 | 5% | 4% | 5% | 5% | 5% |
| -1.2 (adjusted difference) | 6.5 | half | -2.4 | 1.20 | 5% | 5% | 6% | 5% | 6% |
| -1.2 (adjusted difference) | 6.5 | quarter | -4.8 | 2.08 | 9% | 8% | 5% | 5% | 9% |

### Responder effect a half split would need for 80% power

| Trial design | n | SD of change | Method | Responder effect needed (outcome units) | In SDs of change |
|---|---|---|---|---|---|
| ReBUILD (clemastine) | 50 | 5 | Outside noise, estimated from 39 people | 12.5 | 2.5 SD |
| ReBUILD (clemastine) | 50 | 5 | Outside noise, known exactly | 10 | 2 SD |
| ReBUILD (clemastine) | 50 | 5 | Mixture bootstrap LRT | 17.5 | 3.5 SD |
| CCMR One (bexarotene), lesional MTR | 52 | 0.84 | Variance-ratio F test | 2.52 | 3 SD |
| CCMR One (bexarotene), lesional MTR | 52 | 0.84 | Brown-Forsythe test | 2.52 | 3 SD |
| CCMR One (bexarotene), lesional MTR | 52 | 0.84 | Mixture bootstrap LRT | 4.2 | 5 SD |
| CCMR One (bexarotene), VEP | 28 | 5 | Variance-ratio F test | 17.5 | 3.5 SD |
| CCMR One (bexarotene), VEP | 28 | 5 | Brown-Forsythe test | 17.5 | 3.5 SD |
| CCMR One (bexarotene), VEP | 28 | 5 | Mixture bootstrap LRT | 30 | 6 SD |
| CCMR Two (metformin + clemastine) | 67 | 5 | Variance-ratio F test | 12.5 | 2.5 SD |
| CCMR Two (metformin + clemastine) | 67 | 5 | Brown-Forsythe test | 12.5 | 2.5 SD |
| CCMR Two (metformin + clemastine) | 67 | 5 | Mixture bootstrap LRT | 20 | 4 SD |

## What the trial design tables show

- **ReBUILD design (crossover, 50 people).** From the trial's own data alone there is no test:
  response spread and noise cannot be separated. With an outside noise estimate from 39 people, a
  half split of the 1.7 ms effect is detected in 7% to 14% of simulated trials. With the noise
  known exactly, 10% to 23%. With the larger 3.2 ms estimate, 17% to 51% and 30% to 86%. The
  mixture check stays at 5% to 7%.
- **CCMR One design (parallel, 26 per arm), MTR.** A half split of the 0.16 pu effect is detected
  in 5% to 6% of trials. That is the false-positive rate. The design carries no information on
  this question for an effect that small.
- **CCMR One design, VEP in the 28 participants with delayed eyes.** A half split of the
  4.06 ms effect is detected in 12% to 36% of trials by the variance tests and 6% to 7% by the
  mixture check.
- **CCMR Two design (parallel, 33 and 34).** A half split of the 1.2 ms effect is detected in
  5% to 16% of trials. At the protocol's planning SD of 5 ms it is 6% to 7%.
- **What it would take.** For 80% power on a half split, responders would have to improve by 2 to
  3.5 SDs of change. At an SD of 5 ms that is 10 to 17.5 ms in responders, against reported mean
  effects of 1.2 to 4.1 ms. The search used a coarse grid (1, 1.5, 2, ... 4, 5, 6 SDs) at the
  middle SD of each sweep, so these are the first grid values that reach 80%.
- **Moderators.** If responder status closely follows a pre-specified covariate (r=0.7), the
  moderator analysis has 6% to 26% power for a half split of the primary estimates (64% only for
  the 3.2 ms ReBUILD estimate at the lowest noise). If it does not, the moderator analysis cannot
  see responders at all.

## Two checks on published summary numbers

These use published SDs, not participant data. Output: `results/summary_statistic_checks.json`.

- **CCMR One, lesional MTR.** SD of change 0.98 pu on bexarotene and 0.84 pu on placebo, 26 per arm
  assumed. Variance ratio 1.36 (95% CI 0.61 to 3.04), one-sided p = 0.22. SD of individual response
  0.50 pu (95% CI -0.64 to 0.96). The interval includes zero and negative values. No evidence
  either way, as the power table predicts.
- **ReBUILD, VEP.** The registry reports SD of change 6.85 ms in clemastine periods and 3.86 ms in
  placebo periods (93 eyes). The variance ratio is 3.15. **This is a description, not a test.** The
  two columns hold the same 50 people, two eyes each, over periods of different length, and half
  of them had placebo after treatment. None of the methods here is valid for those numbers, and
  the difference has several explanations besides individual response. It is recorded because it
  is the one published hint that spread differed, and because only participant-level data could
  say what it means.

## Limits of this validation

- The simulator's truth is two clean groups. Real response, if it varies, is likely graded. A graded
  response of the same SD is about as visible to the variance tests and less visible to the
  mixture check.
- Noise is the same for everyone and the same in both arms. If treatment changes measurement
  noise (for example through fatigue during recording), the variance tests read that as
  individual response.
- One heavy-tailed case was run (t, 5 degrees of freedom). Skewed noise was not.
- The crossover results assume no carryover. Carryover was not swept.
- Per-eye and per-lesion clustering was not simulated.
- Dropout was not simulated.
