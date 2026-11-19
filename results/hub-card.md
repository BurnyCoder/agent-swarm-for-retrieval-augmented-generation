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
| dev | code | arctic | 2 / 2 | 82.5 [82.0, 83.0] | 0.0028 | 39.1 / 40.9 | 0 |
| dev | code | oneshot | 2 / 2 | 81.0 [78.0, 84.0] | 0.0008 | 7.8 / 9.4 | 0 |
| dev | code | stock | 1 / 1 | 80.0 [80.0, 80.0] | 0.0030 | 75.3 / 75.3 | 0 |
| dev | code | swarm1 | 2 / 2 | 83.0 [80.0, 86.0] | 0.0017 | 32.0 / 37.9 | 0 |
| dev | code | swarm2 | 1 / 1 | 53.0 [53.0, 53.0] | 0.0050 | 57.0 / 57.0 | 0 |
| dev | code | swarm4 | 1 / 1 | 83.0 [83.0, 83.0] | 0.0161 | 127.1 / 127.1 | 0 |
| dev | code | swarm8 | 1 / 1 | 86.0 [86.0, 86.0] | 0.0175 | 104.9 / 104.9 | 0 |
| dev | news | arctic | 10 / 10 | 70.0% [39.7%, 89.2%] | 0.0074 | 41.5 / 97.1 | 0 |
| dev | news | oneshot | 10 / 10 | 70.0% [39.7%, 89.2%] | 0.0007 | 6.7 / 8.3 | 0 |
| dev | news | stock | 10 / 10 | 90.0% [59.6%, 98.2%] | 0.0054 | 63.1 / 126.0 | 0 |
| dev | news | swarm1 | 10 / 10 | 50.0% [23.7%, 76.3%] | 0.0060 | 87.7 / 120.4 | 0 |
| dev | news | swarm2 | 10 / 10 | 60.0% [31.3%, 83.2%] | 0.0091 | 154.1 / 251.0 | 0 |
| dev | news | swarm4 | 10 / 10 | 80.0% [49.0%, 94.3%] | 0.0182 | 179.0 / 228.5 | 0 |
| dev | news | swarm8 | 10 / 10 | 60.0% [31.3%, 83.2%] | 0.0222 | 148.3 / 225.8 | 0 |

¹ Conservative inference charge using the cache-write upper rate for unclassified input tokens. Grading is included in the phase ledger.
