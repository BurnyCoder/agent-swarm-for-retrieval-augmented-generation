# Luna folder research swarm

A private experiment in answering questions from files. Independent GPT-6 Luna investigators use Codex to search a read-only folder. A coordinator checks their source excerpts and writes a cited answer. The experiment varies the total number of agents and measures answer quality, evidence support, time, and API cost on news and Python repositories.

<!-- result-headline -->
## Current held-out results

**2026-11-19 19:38 UTC.** The study has recorded **1,155/2,350 evaluations (49.1%)**. All five methods have scores on 230 questions. The development sweep selected 4 total agents, including the coordinator.

| Matched panel | Questions | 4-agent swarm | One agent | Stock Codex | Arctic single agent | One-shot RAG |
| --- | --- | --- | --- | --- | --- | --- |
| News, first attempts | 156 | 116/156 | 105/156 | 128/156 | 121/156 | 112/156 |
| News, outage-free | 151 | 116/151 | 105/151 | 128/151 | 119/151 | 111/151 |
| Code, first attempts | 74 | 75.53 | 73.92 | 79.20 | 80.15 | 68.30 |
| Code, outage-free | 71 | 77.58 | 77.04 | 81.28 | 82.31 | 69.06 |

News cells count exact matches. Code cells give the mean blinded rubric score out of 100. The primary scores retain 30 provider-overload failures. The outage-free rows exclude a question from all five methods whenever any arm had a recorded overload failure. [Paired outage analysis](reports/experiments/availability.md)

Across 133 outage-free news questions with annotated sources, the swarm cited 85.7% of the reference files per question on average. One agent cited 77.1% and stock Codex cited 82.1%. [Citation and claim-support measurements](reports/experiments/grounding.md)

On the 151 matched outage-free news questions, the swarm took a median **138 seconds** at a mean upper cost of **$0.0171 per question**. Stock Codex took **70 seconds** at **$0.0051**.

The study ledger shows **$9.04 settled** and **$3.85 reserved** against the $50 ceiling. The fixed evidence audit has 0/235 records. [Live local dashboard](http://127.0.0.1:8765) · [Private explorer](https://huggingface.co/spaces/BurnyCoder/luna-folder-swarm-explorer)

The registered comparison is in progress. The available scores are descriptive. [Measured tables](results/tables.md)
<!-- /result-headline -->

The starting observation comes from a small, model-specific study. Its single agent outscored its swarm on repository questions. Its filename-recall measure leaves open whether an agent saw a passage that substantiates the answer. The present comparison holds the generation model fixed, includes ordinary Codex and one-shot retrieval, and measures passage delivery. [Arctic results](https://github.com/BurnyCoder/arcticswarm-folder-rag-research/blob/bd5b3ed98cde10e9c1f90795f2182d84ecd51ddc/results/day1/tables.md) · [Original collector](https://github.com/BurnyCoder/arcticswarm-folder-rag-research/blob/bd5b3ed98cde10e9c1f90795f2182d84ecd51ddc/src/folderrag/collect.py#L78)

## Research record

- [Literature review](reports/literature-review.md) and [state of the art](reports/state-of-the-art-review.md)
- [Preregistration](reports/preregistration.md) and [implementation plan](reports/plan.md)
- [Development amendments](reports/development-amendments.md), [CLI checks](reports/experiments/cli-smoke.md) and [archived Haiku answers under the common scorer](reports/experiments/historical.md)
- [Private collection and encoder](https://huggingface.co/collections/BurnyCoder/luna-folder-swarm-research-6afef1463801afdd0f8b15c0) and [private research artifacts and transcripts](https://huggingface.co/datasets/BurnyCoder/luna-folder-swarm-results)

## Reproduction

The runtime is Linux with bubblewrap, ripgrep, Codex CLI, Python 3.12 and uv. Windows users can run it with WSL2. A GPU accelerates the local Qwen embedding encoder. Keep the OpenAI API key in an ignored project-root `.env`. The host process handles credentials. Each research arm receives only its question and permitted corpus. The budget covers all paid inference and grading for this study. [Codex CLI](https://learn.chatgpt.com/docs/non-interactive-mode) · [Luna](https://developers.openai.com/api/docs/models/gpt-6-luna) · [Qwen model card](https://huggingface.co/Qwen/Qwen3-Embedding-0.6B)

Run `uv run folderrag ask --folder PATH --agents 4 "QUESTION"`. Choose 1, 2, 4 or 8 total agents. At size four, three independent investigators gather evidence and one coordinator verifies quotations and produces the answer. Add `--json` for the answer, citations, offsets, worker completions, time and cost.

![Luna investigator and coordinator architecture](reports/figures/architecture.png)

[Installation, live dashboard and reproduction commands](docs/usage.md) · [Frozen question manifest](protocol/splits.json) · [Private results and examples](https://huggingface.co/spaces/BurnyCoder/luna-folder-swarm-explorer)

## Research milestones

- [x] Register the protocol and ordered, stratified evaluation design.
- [x] Implement the swarm, four sizes, baselines, cost ledger, and source validation.
- [x] Complete the development sweep and freeze the candidate size and affordable test set.
- [ ] Complete the paired confirmation, controls, intervention tests and evidence audit.

<!-- generated -->
## Measured results

Each row uses every graded response available for that method. During collection, methods can have different question counts. Run `uv run folderrag report` to regenerate this snapshot from the saved records.

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

![Answer quality by total Luna agent count](reports/figures/swarm-size.png)

![Scores for fixed example questions](reports/figures/examples.png)

[Read the actual answers and source quotations](reports/experiments/output-examples.md)

[Paper](reports/paper.pdf) · [All experiment reports](reports/summary.md)
