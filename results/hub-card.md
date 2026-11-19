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
| dev | code | arctic | 4 / 4 | 81.0 [78.2, 82.8] | 0.0026 | 39.1 / 44.8 | 0 |
| dev | code | oneshot | 5 / 5 | 80.2 [78.2, 82.4] | 0.0007 | 8.3 / 10.7 | 0 |
| dev | code | stock | 4 / 4 | 79.8 [71.0, 86.5] | 0.0040 | 68.9 / 92.0 | 0 |
| dev | code | swarm1 | 4 / 4 | 81.0 [78.0, 84.5] | 0.0028 | 37.9 / 58.7 | 0 |
| dev | code | swarm2 | 4 / 4 | 64.5 [49.0, 80.0] | 0.0055 | 63.5 / 186.1 | 0 |
| dev | code | swarm4 | 4 / 4 | 77.0 [69.5, 83.0] | 0.0165 | 146.0 / 222.2 | 0 |
| dev | code | swarm8 | 4 / 4 | 76.8 [65.2, 85.0] | 0.0204 | 127.1 / 165.6 | 0 |
| dev | news | arctic | 10 / 10 | 70.0% [39.7%, 89.2%] | 0.0074 | 41.5 / 97.1 | 0 |
| dev | news | oneshot | 10 / 10 | 70.0% [39.7%, 89.2%] | 0.0007 | 6.7 / 8.3 | 0 |
| dev | news | stock | 10 / 10 | 90.0% [59.6%, 98.2%] | 0.0054 | 63.1 / 126.0 | 0 |
| dev | news | swarm1 | 10 / 10 | 50.0% [23.7%, 76.3%] | 0.0060 | 87.7 / 120.4 | 0 |
| dev | news | swarm2 | 10 / 10 | 60.0% [31.3%, 83.2%] | 0.0091 | 154.1 / 251.0 | 0 |
| dev | news | swarm4 | 10 / 10 | 80.0% [49.0%, 94.3%] | 0.0182 | 179.0 / 228.5 | 0 |
| dev | news | swarm8 | 10 / 10 | 60.0% [31.3%, 83.2%] | 0.0222 | 148.3 / 225.8 | 0 |

¹ Conservative inference charge using the cache-write upper rate for unclassified input tokens. Grading is included in the phase ledger.
