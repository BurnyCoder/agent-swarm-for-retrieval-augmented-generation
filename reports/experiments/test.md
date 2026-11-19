# Test experiments

The frozen size and three external baselines share the same confirmatory questions. The one-agent counterpart isolates the effect of delegation.

| Phase | Domain | Method | Graded / attempts | Quality [95% CI] | USD/question¹ | Median / p95 s | Errors |
|---|---|---|---:|---:|---:|---:|---:|
| test | code | arctic | 81 / 81 | 80.4 [76.7, 83.3] | 0.0055 | 55.1 / 142.8 | 2 |
| test | code | oneshot | 81 / 81 | 67.9 [63.7, 71.9] | 0.0008 | 9.2 / 18.0 | 0 |
| test | code | stock | 81 / 81 | 79.3 [75.5, 82.2] | 0.0046 | 72.4 / 122.7 | 2 |
| test | code | swarm1 | 81 / 81 | 74.5 [70.3, 78.2] | 0.0055 | 74.7 / 177.8 | 3 |
| test | code | swarm4 | 81 / 81 | 76.0 [72.2, 79.3] | 0.0172 | 146.5 / 238.0 | 2 |
| test | news | arctic | 169 / 169 | 78.1% [71.3%, 83.7%] | 0.0066 | 36.2 / 73.9 | 3 |
| test | news | oneshot | 169 / 169 | 71.0% [63.8%, 77.3%] | 0.0008 | 7.7 / 11.9 | 4 |
| test | news | stock | 169 / 169 | 82.8% [76.4%, 87.8%] | 0.0052 | 70.4 / 111.8 | 5 |
| test | news | swarm1 | 169 / 169 | 68.6% [61.3%, 75.2%] | 0.0059 | 75.7 / 169.8 | 5 |
| test | news | swarm4 | 169 / 169 | 74.6% [67.5%, 80.5%] | 0.0174 | 138.2 / 207.7 | 4 |

¹ Conservative inference charge using the cache-write upper rate for unclassified input tokens. Grading is included in the phase ledger.

- news against stock, n=169, difference -0.0828, 95% CI [-0.1420, -0.0296], Holm p=0.04678.
- news against arctic, n=169, difference -0.0355, 95% CI [-0.0947, 0.0237], Holm p=0.6899.
- news against oneshot, n=169, difference 0.0355, 95% CI [-0.0296, 0.1006], Holm p=0.6899.
- news against swarm1, n=169, difference 0.0592, 95% CI [-0.0118, 0.1302], Holm p=0.2866.
- code against stock, n=81, difference -3.2716, 95% CI [-6.8148, 0.2843], Holm p=0.2826.
- code against arctic, n=81, difference -4.3704, 95% CI [-7.5926, -1.1975], Holm p=0.04678.
- code against oneshot, n=81, difference 8.0864, 95% CI [3.4444, 12.5559], Holm p=0.0126.
- code against swarm1, n=81, difference 1.4691, 95% CI [-1.1975, 4.3333], Holm p=0.3694.