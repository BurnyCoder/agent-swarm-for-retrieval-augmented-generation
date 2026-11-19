# Source grounding

¹ Mean per-question recall on questions with annotated files. Returned-file recall depends on path visibility in each tool interface. ² Citation support includes one failed opportunity for each answer without citations. Exact quote matching, assertion support, and annotated fact exposure have different denominators.

| Phase | Domain | Method | Answers | Literal quotes valid | Answers with citations | Gold files returned¹ | Gold files cited¹ |
| --- | --- | --- | --- | --- | --- | --- | --- |
| dev | code | arctic | 4 | 10/13 (76.9%) | 4/4 (100.0%) | — | — |
| dev | code | oneshot | 5 | 13/13 (100.0%) | 5/5 (100.0%) | — | — |
| dev | code | stock | 4 | 10/13 (76.9%) | 4/4 (100.0%) | — | — |
| dev | code | swarm1 | 4 | 8/8 (100.0%) | 4/4 (100.0%) | — | — |
| dev | code | swarm2 | 4 | 6/9 (66.7%) | 4/4 (100.0%) | — | — |
| dev | code | swarm4 | 4 | 12/12 (100.0%) | 4/4 (100.0%) | — | — |
| dev | code | swarm8 | 4 | 14/14 (100.0%) | 4/4 (100.0%) | — | — |
| dev | news | arctic | 10 | 30/33 (90.9%) | 10/10 (100.0%) | 96.3% | 80.6% |
| dev | news | oneshot | 10 | 24/26 (92.3%) | 9/10 (90.0%) | 73.1% | 66.7% |
| dev | news | stock | 10 | 32/33 (97.0%) | 10/10 (100.0%) | 86.1% | 86.1% |
| dev | news | swarm1 | 10 | 34/36 (94.4%) | 10/10 (100.0%) | 88.9% | 86.1% |
| dev | news | swarm2 | 10 | 30/33 (90.9%) | 10/10 (100.0%) | 86.1% | 78.7% |
| dev | news | swarm4 | 10 | 36/36 (100.0%) | 10/10 (100.0%) | 92.6% | 84.3% |
| dev | news | swarm8 | 10 | 36/37 (97.3%) | 10/10 (100.0%) | 88.9% | 86.1% |

| Domain | Method | Audited | Citation support² | Factual assertions supported | Answers without citations | Gold facts shown | Definition citations | Call citations |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
