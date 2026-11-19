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
