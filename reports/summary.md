# Experiment summary

The 4-agent swarm answered 126/169 news questions correctly and averaged 76.00/100 on code. The highest observed news score came from stock Codex (140/169). The highest observed code score came from Arctic single agent (80.37/100). One investigator scored 116/169 on news and 74.53/100 on code. The swarm's code difference from one-shot retrieval was +8.09 points. Both paired intervals for adding investigators include zero. The shortened panel supports exploratory paired estimates. The original full-sample superiority claim remains unresolved.

Paid acquisition stopped at the owner's request after interim scores were visible. Today's panel uses the first 250 of the 470 questions in the frozen order (169 news and 81 code). The archive preserves 37 additional completed answers from 9 later questions outside the analysis. The spending ledger includes those answers and interrupted calls. The remaining questions, controls, repeats, changed-fact tests and semantic evidence audits are postponed.

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

- [Experiment inventory](experiments/inventory.md)
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
- [End-of-day results and stopping decision](experiments/closeout.md)
- [News citation address audit](experiments/offsets.md)
