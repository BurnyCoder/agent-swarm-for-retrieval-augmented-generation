# Test experiments

The frozen size and three external baselines share the same confirmatory questions. The one-agent counterpart isolates the effect of delegation.

| Phase | Domain | Method | Graded / attempts | Quality [95% CI] | USD/question¹ | Median / p95 s | Errors |
|---|---|---|---:|---:|---:|---:|---:|
| test | code | arctic | 74 / 74 | 80.1 [76.1, 83.4] | 0.0056 | 55.5 / 141.4 | 2 |
| test | code | oneshot | 74 / 74 | 68.3 [64.0, 72.4] | 0.0008 | 9.4 / 18.0 | 0 |
| test | code | stock | 74 / 74 | 79.2 [75.0, 82.4] | 0.0046 | 70.4 / 120.7 | 2 |
| test | code | swarm1 | 74 / 74 | 73.9 [69.2, 77.9] | 0.0054 | 73.9 / 181.6 | 3 |
| test | code | swarm4 | 74 / 74 | 75.5 [71.5, 79.1] | 0.0172 | 143.5 / 240.0 | 2 |
| test | news | arctic | 159 / 159 | 78.0% [70.9%, 83.7%] | 0.0065 | 36.2 / 76.8 | 3 |
| test | news | oneshot | 158 / 158 | 72.2% [64.7%, 78.6%] | 0.0008 | 7.7 / 12.1 | 4 |
| test | news | stock | 156 / 156 | 82.1% [75.3%, 87.3%] | 0.0052 | 70.4 / 110.3 | 5 |
| test | news | swarm1 | 156 / 156 | 67.3% [59.6%, 74.2%] | 0.0075 | 73.9 / 144.6 | 5 |
| test | news | swarm4 | 156 / 156 | 74.4% [67.0%, 80.6%] | 0.0174 | 136.4 / 203.3 | 4 |

¹ Conservative inference charge using the cache-write upper rate for unclassified input tokens. Grading is included in the phase ledger.

