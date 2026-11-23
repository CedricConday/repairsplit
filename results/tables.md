## Known-answer tables

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

## Trial design tables

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

