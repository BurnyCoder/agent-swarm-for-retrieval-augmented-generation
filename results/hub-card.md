---
language:
- en
task_categories:
- question-answering
tags:
- retrieval-augmented-generation
- multi-agent
- evaluation
---

# Luna folder swarm research

Private research records for a preregistered comparison of single and multi-agent file search. Each condition uses GPT-6 Luna. Codex investigators search an isolated folder and send evidence to a coordinator. The experiment varies total agent count and includes stock Codex, Arctic B2, one-shot retrieval, controls and ablations.

See the [preregistration](reports/preregistration.md), [measured tables](results/tables.md), [paper](reports/paper.pdf) and [private results explorer](https://huggingface.co/spaces/BurnyCoder/luna-folder-swarm-explorer). The [private GitHub repository](https://github.com/BurnyCoder/agent-swarm-for-retrieval-augmented-generation) contains the exact implementation and pinned Arctic submodule. The source archive contains Git-tracked files. Benchmark sources retain their individual licenses. The case records distinguish development, confirmation and diagnostics.


## Current measurements

The registered comparison is in progress. The available scores are descriptive.

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
