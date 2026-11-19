# Test experiments

The frozen size and three external baselines share the same confirmatory questions. The one-agent counterpart isolates the effect of delegation.

| Phase | Domain | Method | Graded / attempts | Quality [95% CI] | USD/question¹ | Median / p95 s | Errors |
|---|---|---|---:|---:|---:|---:|---:|
| test | code | arctic | 79 / 79 | 80.4 [76.7, 83.3] | 0.0055 | 55.1 / 140.9 | 2 |
| test | code | oneshot | 81 / 81 | 67.9 [63.7, 71.9] | 0.0008 | 9.2 / 18.0 | 0 |
| test | code | stock | 80 / 80 | 79.2 [75.5, 82.3] | 0.0046 | 71.4 / 123.0 | 2 |
| test | code | swarm1 | 81 / 81 | 74.5 [70.3, 78.2] | 0.0055 | 74.7 / 177.8 | 3 |
| test | code | swarm4 | 79 / 79 | 76.0 [72.0, 79.2] | 0.0172 | 145.5 / 238.6 | 2 |
| test | news | arctic | 166 / 166 | 77.7% [70.8%, 83.4%] | 0.0066 | 36.2 / 74.3 | 3 |
| test | news | oneshot | 166 / 166 | 71.7% [64.4%, 78.0%] | 0.0008 | 7.7 / 12.0 | 4 |
| test | news | stock | 166 / 166 | 82.5% [76.0%, 87.6%] | 0.0052 | 70.4 / 111.1 | 5 |
| test | news | swarm1 | 165 / 165 | 67.9% [60.4%, 74.5%] | 0.0075 | 75.0 / 167.1 | 5 |
| test | news | swarm4 | 165 / 165 | 74.5% [67.4%, 80.6%] | 0.0174 | 137.6 / 207.9 | 4 |

¹ Conservative inference charge using the cache-write upper rate for unclassified input tokens. Grading is included in the phase ledger.

