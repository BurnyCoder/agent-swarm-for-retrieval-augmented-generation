# End-of-day results and stopping decision

Paid acquisition stopped at the owner's request after interim scores were visible. Today's panel uses the first 250 of the 470 questions in the frozen order (169 news and 81 code). The archive preserves 37 additional completed answers from 9 later questions outside the analysis. The spending ledger includes those answers and interrupted calls. The remaining questions, controls, repeats, changed-fact tests and semantic evidence audits are postponed. Every retained question has a grade for every method. The scores include 30 first-attempt generation failures.

The 4-agent swarm answered 126/169 news questions correctly and averaged 76.00/100 on code. The highest observed news score came from stock Codex (140/169). The highest observed code score came from Arctic single agent (80.37/100). One investigator scored 116/169 on news and 74.53/100 on code. The swarm's code difference from one-shot retrieval was +8.09 points. Both paired intervals for adding investigators include zero. The shortened panel supports exploratory paired estimates. The original full-sample superiority claim remains unresolved.

### Quality on matched questions

| Method | News (n=169) | News outage-free (n=164) | Code (n=81) | Code outage-free (n=78) |
| --- | --- | --- | --- | --- |
| 4-agent swarm | 126/169 (74.6%) | 126/164 (76.8%) | 76.00 | 77.88 |
| 1-agent harness | 116/169 (68.6%) | 116/164 (70.7%) | 74.53 | 77.40 |
| Stock Codex | 140/169 (82.8%) | 140/164 (85.4%) | 79.27 | 81.17 |
| Arctic single agent | 132/169 (78.1%) | 130/164 (79.3%) | 80.37 | 82.35 |
| One-shot hybrid RAG | 120/169 (71.0%) | 119/164 (72.6%) | 67.91 | 68.59 |

### Mean generation cost and median latency on first attempts

| Method | News USD / question | News median s | Code USD / question | Code median s |
| --- | --- | --- | --- | --- |
| 4-agent swarm | $0.01739 | 138.2 | $0.01721 | 146.5 |
| 1-agent harness | $0.00593 | 75.7 | $0.00552 | 74.7 |
| Stock Codex | $0.00521 | 70.4 | $0.00463 | 72.4 |
| Arctic single agent | $0.00655 | 36.2 | $0.00545 | 55.1 |
| One-shot hybrid RAG | $0.00079 | 7.7 | $0.00079 | 9.2 |

### Swarm size on each sample

| Agents | Development news | Development code | Held-out news | Held-out code |
| --- | --- | --- | --- | --- |
| 1 | 5/10 | 82.60 (n=10) | 116/169 | 74.53 (n=81) |
| 2 | 6/10 | 71.60 (n=10) | Postponed | Postponed |
| 4 | 8/10 | 75.10 (n=10) | 126/169 | 76.00 (n=81) |
| 8 | 6/10 | 78.90 (n=10) | Postponed | Postponed |

### Paired differences

Differences below subtract the comparator from the selected swarm. News uses percentage points and code uses rubric points. The six external comparisons and the two size comparisons use their prespecified, separate Holm families. These estimates and intervals are exploratory after the owner-directed stop.

| Domain | Comparator | Pairs | Difference | Paired 95% interval | Holm p | Repository bootstrap 95% interval |
| --- | --- | --- | --- | --- | --- | --- |
| news | stock | 169 | -8.28 | -14.20 to -2.96 | 0.04678 | — |
| news | arctic | 169 | -3.55 | -9.47 to +2.37 | 0.6899 | — |
| news | oneshot | 169 | +3.55 | -2.96 to +10.06 | 0.6899 | — |
| news | swarm1 | 169 | +5.92 | -1.18 to +13.02 | 0.2866 | — |
| code | stock | 81 | -3.27 | -6.81 to +0.28 | 0.2826 | -6.12 to -0.65 |
| code | arctic | 81 | -4.37 | -7.59 to -1.20 | 0.04678 | -7.85 to -1.14 |
| code | oneshot | 81 | +8.09 | +3.44 to +12.56 | 0.0126 | +2.65 to +13.05 |
| code | swarm1 | 81 | +1.47 | -1.20 to +4.33 | 0.3694 | -1.56 to +4.04 |

[Experiment inventory](inventory.md) · [Outage-free sensitivity](availability.md) · [Exact citation audit](grounding.md) · [Frozen cutoff IDs and excluded record IDs](../../protocol/closeout.json)
