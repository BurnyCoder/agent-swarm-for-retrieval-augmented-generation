# Source grounding

¹ Mean per-question recall on questions with annotated files. Returned-file recall depends on path visibility in each tool interface. ² Citation support includes one failed opportunity for each answer without citations. Exact quote matching, assertion support, and annotated fact exposure have different denominators.

| Phase | Domain | Method | Answers | Literal quotes valid | Answers with citations | Gold files returned¹ | Gold files cited¹ |
| --- | --- | --- | --- | --- | --- | --- | --- |
| dev | news | arctic | 8 | 26/28 (92.9%) | 8/8 (100.0%) | 95.2% | 82.1% |
| dev | news | oneshot | 9 | 21/23 (91.3%) | 8/9 (88.9%) | 69.8% | 62.5% |
| dev | news | stock | 9 | 29/30 (96.7%) | 9/9 (100.0%) | 84.4% | 84.4% |
| dev | news | swarm1 | 8 | 27/29 (93.1%) | 8/8 (100.0%) | 85.7% | 82.1% |
| dev | news | swarm2 | 8 | 24/27 (88.9%) | 8/8 (100.0%) | 82.1% | 72.6% |
| dev | news | swarm4 | 9 | 33/33 (100.0%) | 9/9 (100.0%) | 91.7% | 82.3% |
| dev | news | swarm8 | 9 | 34/35 (97.1%) | 9/9 (100.0%) | 87.5% | 84.4% |

| Domain | Method | Audited | Citation support² | Factual assertions supported | Answers without citations | Gold facts shown | Definition citations | Call citations |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
