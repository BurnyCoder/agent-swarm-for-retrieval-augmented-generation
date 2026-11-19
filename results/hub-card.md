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

Research records for a preregistered comparison of single-agent and multi-agent file search with GPT-6 Luna. Codex investigators search an isolated folder and send evidence to a coordinator. The held-out comparison includes stock Codex, Arctic’s single agent and one-shot retrieval. The experiment inventory identifies the postponed controls and ablations.

Download the paper, scores and benchmark transcripts, or inspect individual answers in the explorer. [Paper](https://huggingface.co/datasets/BurnyCoder/luna-folder-swarm-results/resolve/main/reports/paper.pdf) · [Tables](https://huggingface.co/datasets/BurnyCoder/luna-folder-swarm-results/blob/main/results/tables.md) · [Transcripts](https://huggingface.co/datasets/BurnyCoder/luna-folder-swarm-results/tree/main/traces) · [Explorer](https://huggingface.co/spaces/BurnyCoder/luna-folder-swarm-explorer) · [Source and preregistration](https://github.com/BurnyCoder/agent-swarm-for-retrieval-augmented-generation)

The news benchmark uses Tang and Yang’s MultiHop-RAG database under the Open Data Commons Attribution License. The underlying articles retain their publishers’ rights. The SWE-QA benchmark and rubric use Apache-2.0, and the pinned code repositories retain their respective licenses. [MultiHop-RAG](https://github.com/yixuantt/MultiHop-RAG#license) · [ODC-By 1.0](https://opendatacommons.org/licenses/by/1-0/) · [SWE-QA](https://github.com/peng-weihan/SWE-QA-Bench)


## Current measurements

The 4-agent swarm answered 126/169 news questions correctly and averaged 76.00/100 on code. The highest observed news score came from stock Codex (140/169). The highest observed code score came from Arctic single agent (80.37/100). One investigator scored 116/169 on news and 74.53/100 on code. The swarm's code difference from one-shot retrieval was +8.09 points. Both paired intervals for adding investigators include zero. The shortened panel supports exploratory paired estimates. The original full-sample superiority claim remains unresolved.

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
