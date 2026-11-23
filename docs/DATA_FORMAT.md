# Input format

`repairsplit analyze` reads one tidy CSV. One row is one outcome measurement.

| Column | Parallel trial | Crossover trial | Meaning |
|---|---|---|---|
| `participant` | required | required | Any ID. Must not identify a person. |
| `arm` | required | leave empty | Two labels. The treated arm is `treatment` unless `--treatment-label` says otherwise. |
| `sequence` | leave empty | required | `TC` = treatment in period 1, control in period 2. `CT` = the reverse. |
| `period` | optional | required | `1` or `2`. |
| `baseline` | required | optional | Value before any treatment. |
| `outcome` | required | required | Value at the end of treatment (parallel) or at the end of that period (crossover). |
| any other column | optional | optional | Numeric covariates, usable as moderators by name (for example `age`). |

Rules:

- Parallel: one row per participant. The analysed value is the change score, `outcome - baseline`.
- Crossover: two rows per participant, one per period. The analysed value is the within-person
  difference, treated outcome minus control outcome. `baseline` is not used for that difference,
  but it can be named as a moderator. Covariates are read from the participant's first row.
- The design is detected from the columns: a filled `sequence` column means crossover, otherwise
  a filled `arm` column means parallel. `--design` overrides this.
- One value per participant and visit. If the outcome is measured per eye or per lesion, reduce it
  to one number per participant first (for example the mean over eligible eyes). The methods assume
  independent participants. Rows from the same person are not independent.
- Participants with a missing `baseline` or `outcome` (parallel) or a missing period (crossover)
  are dropped. Nothing is imputed.
- Replicated crossovers (more than two periods) are not supported in this version.
- Units are up to you. All spreads are reported in the units of `outcome`.

`repairsplit simulate` writes this layout, plus a `true_responder` column that holds the known
answer. `analyze` ignores that column unless you name it as a moderator, which you should not.

## Example, parallel

```
participant,arm,sequence,period,baseline,outcome,age
P0001,treatment,,1,131.2,124.9,44
P0002,control,,1,127.5,128.1,39
```

## Example, crossover

```
participant,arm,sequence,period,baseline,outcome,age
P0001,,TC,1,131.2,125.0,44
P0001,,TC,2,131.2,130.4,44
P0002,,CT,1,127.5,128.3,39
P0002,,CT,2,127.5,126.9,39
```

## Outside test-retest noise (crossover only)

A two-period crossover cannot separate individual response from measurement noise. If a
test-retest study of the same measurement exists, pass its result:

- `--retest-sd-diff X`: SD of the difference between two measurements on the same untreated
  person. Or `--retest-sd-within X`: SD of a single measurement around the person's own level
  (the tool multiplies by the square root of 2).
- `--retest-df N`: people in that study minus one. Without it the noise is treated as known
  exactly, which makes the result look more certain than it is.

The time gap, equipment and kind of patient in the outside study should match the trial. If they
do not, the subtraction is not valid and the tool cannot tell.
