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
| dev | news | arctic | 8 / 8 | 75.0% [40.9%, 92.9%] | 0.0082 | 42.7 / 104.4 | 0 |
| dev | news | oneshot | 9 / 9 | 77.8% [45.3%, 93.7%] | 0.0007 | 6.3 / 8.3 | 0 |
| dev | news | stock | 9 / 9 | 88.9% [56.5%, 98.0%] | 0.0052 | 55.8 / 128.1 | 0 |
| dev | news | swarm1 | 8 / 8 | 50.0% [21.5%, 78.5%] | 0.0060 | 100.1 / 120.7 | 0 |
| dev | news | swarm2 | 8 / 8 | 50.0% [21.5%, 78.5%] | 0.0101 | 170.2 / 251.7 | 0 |
| dev | news | swarm4 | 9 / 9 | 88.9% [56.5%, 98.0%] | 0.0186 | 180.5 / 230.2 | 0 |
| dev | news | swarm8 | 9 / 9 | 66.7% [35.4%, 87.9%] | 0.0225 | 148.8 / 227.5 | 0 |

¹ Conservative inference charge using the cache-write upper rate for unclassified input tokens. Grading is included in the phase ledger.
