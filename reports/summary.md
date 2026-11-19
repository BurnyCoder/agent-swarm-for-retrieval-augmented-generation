# Experiment summary

The registered comparison is in progress. The available scores are descriptive.

The frozen development choice is **4 agents**, including the coordinator. The cost rule admitted **10 balanced blocks**.

| Phase | Domain | Method | Graded / attempts | Quality [95% CI] | USD/question¹ | Median / p95 s | Errors |
|---|---|---|---:|---:|---:|---:|---:|
| dev | code | arctic | 10 / 10 | 83.1 [81.3, 85.0] | 0.0032 | 39.1 / 136.2 | 0 |
| dev | code | oneshot | 10 / 10 | 78.7 [73.3, 82.9] | 0.0008 | 7.9 / 13.3 | 0 |
| dev | code | stock | 10 / 10 | 81.1 [75.9, 85.3] | 0.0042 | 78.2 / 125.3 | 0 |
| dev | code | swarm1 | 10 / 10 | 82.6 [80.0, 85.4] | 0.0041 | 47.6 / 111.2 | 0 |
| dev | code | swarm2 | 10 / 10 | 71.6 [61.6, 80.6] | 0.0082 | 98.5 / 262.4 | 0 |
| dev | code | swarm4 | 10 / 10 | 75.1 [66.7, 82.3] | 0.0172 | 135.3 / 238.0 | 0 |
| dev | code | swarm8 | 10 / 10 | 78.9 [72.8, 84.2] | 0.0219 | 112.1 / 253.9 | 0 |
| dev | news | arctic | 10 / 10 | 70.0% [39.7%, 89.2%] | 0.0074 | 41.5 / 97.1 | 0 |
| dev | news | oneshot | 10 / 10 | 70.0% [39.7%, 89.2%] | 0.0007 | 6.7 / 8.3 | 0 |
| dev | news | stock | 10 / 10 | 90.0% [59.6%, 98.2%] | 0.0054 | 63.1 / 126.0 | 0 |
| dev | news | swarm1 | 10 / 10 | 50.0% [23.7%, 76.3%] | 0.0060 | 87.7 / 120.4 | 0 |
| dev | news | swarm2 | 10 / 10 | 60.0% [31.3%, 83.2%] | 0.0091 | 154.1 / 251.0 | 0 |
| dev | news | swarm4 | 10 / 10 | 80.0% [49.0%, 94.3%] | 0.0182 | 179.0 / 228.5 | 0 |
| dev | news | swarm8 | 10 / 10 | 60.0% [31.3%, 83.2%] | 0.0222 | 148.3 / 225.8 | 0 |
| test | code | arctic | 10 / 10 | 64.6 [41.2, 83.7] | 0.0147 | 67.0 / 145.7 | 2 |
| test | code | oneshot | 9 / 9 | 65.0 [51.9, 77.8] | 0.0008 | 9.6 / 19.1 | 0 |
| test | code | stock | 10 / 10 | 64.6 [41.2, 82.6] | 0.0056 | 56.9 / 85.4 | 2 |
| test | code | swarm1 | 9 / 9 | 47.8 [24.1, 69.9] | 0.0066 | 53.0 / 166.5 | 3 |
| test | code | swarm4 | 8 / 8 | 55.9 [30.7, 78.1] | 0.0200 | 143.8 / 218.3 | 2 |
| test | news | arctic | 24 / 24 | 54.2% [35.1%, 72.1%] | 0.0151 | 49.9 / 120.5 | 3 |
| test | news | oneshot | 24 / 24 | 41.7% [24.5%, 61.2%] | 0.0013 | 7.5 / 15.4 | 4 |
| test | news | stock | 24 / 24 | 50.0% [31.4%, 68.6%] | 0.0059 | 56.1 / 108.2 | 5 |
| test | news | swarm1 | 24 / 24 | 37.5% [21.2%, 57.3%] | 0.0055 | 57.7 / 132.5 | 5 |
| test | news | swarm4 | 24 / 24 | 45.8% [27.9%, 64.9%] | 0.0195 | 112.4 / 172.2 | 4 |

¹ Conservative inference charge using the cache-write upper rate for unclassified input tokens. Grading is included in the phase ledger.



- [Service availability and technical repeats](experiments/availability.md)
- [Generalization by repository and news type](experiments/strata.md)
- [Execution coverage](experiments/coverage.md)
- [Normal Windows CLI checks](experiments/cli-smoke.md)
- [Investigator turn-limit pilot](experiments/handoff-pilot.md)
- [Historical bridge](experiments/historical.md)
- [Swarm size and participation](experiments/swarm-sizes.md)
- [Source grounding](experiments/grounding.md)
- [File interventions](experiments/counterfactuals.md)
- [Independent repeat runs](experiments/variability.md)
- [Index setup and loading](experiments/indexing.md)
- [News citation address audit](experiments/offsets.md)
