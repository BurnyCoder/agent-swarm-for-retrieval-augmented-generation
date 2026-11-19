# Experiment inventory

Counts come from saved graded runs, audit records, or completed engineering checks as appropriate for each row. The five primary methods share every registered held-out question. The controls use the fixed first block. Technical repeats have their own records and budget. [Preregistration](../preregistration.md) · [Offline test coverage](offline.md)

| Experiment | Type | Status | Recorded / planned | What it tests |
| --- | --- | --- | --- | --- |
| Investigator handoff pilot | Engineering pilot | Completed | 6/6 | Check whether concurrent investigators return their findings before their turn limits. |
| Live CLI checks | End-to-end checks | Completed | 2/2 | Combine two files to answer a question, then abstain when a date is missing. |
| News passage addresses | Deterministic data audit | Completed | 1/1 | Reproduce exact source slices and check for duplicate identifiers on long lines. |
| Historical Arctic comparison | Retrospective rescoring | Completed | 40/40 | Apply the common scorers to archived Haiku single-agent and swarm answers. |
| Development size sweep | Model selection | Completed | 80/80 | Compare sizes 1, 2, 4, and 8 on the same legacy questions before selecting the candidate. |
| Development baselines | Baseline calibration | Completed | 60/60 | Measure stock Codex, Arctic single agent, and one-shot retrieval on the development questions. |
| Four-agent swarm | Confirmatory candidate | In progress | 244/470 | Independent investigators hand verified passages to a coordinator. |
| One-agent harness | Delegation comparison | In progress | 246/470 | Use the same retrieval tools and question-level resource ceiling with one investigator. |
| Stock Codex | File-search baseline | In progress | 246/470 | Let stock Codex investigate the same immutable folder. |
| Arctic single agent | Prior-system baseline | In progress | 245/470 | Run the earlier Arctic B2 agent with the same Luna model and effort. |
| One-shot hybrid RAG | Retrieval baseline | In progress | 247/470 | Generate one answer from a fixed set of hybrid-ranked passages. |
| Held-out 2-agent swarm | Swarm-size comparison | Planned | 0/47 | Measure the other swarm sizes on the fixed first block shared by all four sizes. |
| Held-out 8-agent swarm | Swarm-size comparison | Planned | 0/47 | Measure the other swarm sizes on the fixed first block shared by all four sizes. |
| Closed book | Knowledge control | Planned | 0/47 | Answer without source files to measure what the question and model alone provide. |
| Random passages | Negative control | Planned | 0/47 | Replace relevance ranking with randomly selected passages under the same passage budget. |
| Gold news evidence | Retrieval diagnostic | Planned | 0/28 | Supply annotated evidence for eligible news questions to probe remaining answer errors. |
| Lexical search only | Retrieval ablation | Planned | 0/47 | Disable dense search in the selected swarm and retain lexical search. |
| Verification disabled | Citation ablation | Planned | 0/47 | Disable the citation-repair opportunity in the selected swarm and still score the returned quotes. |
| Independent repeat | Run variability | Planned | 0/8 | Rerun the selected swarm on unchanged documents and compare answers and scores. |
| Changed-fact folders | Causal intervention | Planned | 0/4 | Change the decisive stop count or Requests pool-size constant in a pair of copies of each corpus. |
| Blinded evidence audit | Grounding evaluation | Planned | 0/235 | Assess claim support, uncited assertions, gold fact exposure, and code definitions and calls. |
| Provider-failure repeats | Operational sensitivity | Planned | 0/30 | Repeat eligible upstream failures once within the retry budget. Primary scores keep their first attempts. |
