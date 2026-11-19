# Luna folder research swarm

A private experiment in answering questions from files. Independent GPT-6 Luna investigators use Codex to search a read-only folder. A coordinator checks their source excerpts and writes a cited answer. The experiment varies the total number of agents and measures answer quality, evidence support, time, and API cost on news and Python repositories.

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
- [ ] Complete the development sweep and freeze the candidate size and affordable test set.
- [ ] Complete the paired confirmation, controls, intervention tests and evidence audit.

<!-- generated -->
## Measured results

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

![Scores for fixed example questions](reports/figures/examples.png)

[Read the actual answers and source quotations](reports/experiments/output-examples.md)

[Paper](reports/paper.pdf) · [All experiment reports](reports/summary.md)
