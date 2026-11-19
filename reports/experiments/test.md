# Test experiments

The frozen size and three external baselines share the same confirmatory questions. The one-agent counterpart isolates the effect of delegation.

| Phase | Domain | Method | Graded / attempts | Quality [95% CI] | USD/question¹ | Median / p95 s | Errors |
|---|---|---|---:|---:|---:|---:|---:|
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

