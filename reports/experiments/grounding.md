# Source grounding

¹ Mean per-question recall on questions with annotated files. Returned-file recall depends on path visibility in each tool interface. ² Citation support includes one failed opportunity for each answer without citations. Exact quote matching, assertion support, and annotated fact exposure have different denominators.

| Phase | Domain | Method | Answers | Literal quotes valid | Answers with citations | Gold files returned¹ | Gold files cited¹ |
| --- | --- | --- | --- | --- | --- | --- | --- |
| dev | code | arctic | 10 | 30/39 (76.9%) | 10/10 (100.0%) | — | — |
| dev | code | oneshot | 10 | 26/33 (78.8%) | 10/10 (100.0%) | — | — |
| dev | code | stock | 10 | 31/42 (73.8%) | 10/10 (100.0%) | — | — |
| dev | code | swarm1 | 10 | 34/34 (100.0%) | 10/10 (100.0%) | — | — |
| dev | code | swarm2 | 10 | 34/39 (87.2%) | 10/10 (100.0%) | — | — |
| dev | code | swarm4 | 10 | 36/39 (92.3%) | 10/10 (100.0%) | — | — |
| dev | code | swarm8 | 10 | 43/45 (95.6%) | 10/10 (100.0%) | — | — |
| dev | news | arctic | 10 | 30/33 (90.9%) | 10/10 (100.0%) | 96.3% | 80.6% |
| dev | news | oneshot | 10 | 24/26 (92.3%) | 9/10 (90.0%) | 73.1% | 66.7% |
| dev | news | stock | 10 | 32/33 (97.0%) | 10/10 (100.0%) | 86.1% | 86.1% |
| dev | news | swarm1 | 10 | 34/36 (94.4%) | 10/10 (100.0%) | 88.9% | 86.1% |
| dev | news | swarm2 | 10 | 30/33 (90.9%) | 10/10 (100.0%) | 86.1% | 78.7% |
| dev | news | swarm4 | 10 | 36/36 (100.0%) | 10/10 (100.0%) | 92.6% | 84.3% |
| dev | news | swarm8 | 10 | 36/37 (97.3%) | 10/10 (100.0%) | 88.9% | 86.1% |
| test | code | arctic | 74 | 222/277 (80.1%) | 72/74 (97.3%) | — | — |
| test | code | oneshot | 74 | 161/207 (77.8%) | 73/74 (98.6%) | — | — |
| test | code | stock | 74 | 280/319 (87.8%) | 72/74 (97.3%) | — | — |
| test | code | swarm1 | 74 | 280/298 (94.0%) | 71/74 (95.9%) | — | — |
| test | code | swarm4 | 74 | 309/321 (96.3%) | 72/74 (97.3%) | — | — |
| test | news | arctic | 159 | 414/465 (89.0%) | 143/159 (89.9%) | 95.6% | 78.3% |
| test | news | oneshot | 158 | 315/334 (94.3%) | 141/158 (89.2%) | 71.1% | 61.8% |
| test | news | stock | 156 | 430/478 (90.0%) | 151/156 (96.8%) | 82.1% | 82.1% |
| test | news | swarm1 | 156 | 447/474 (94.3%) | 143/156 (91.7%) | 89.1% | 77.1% |
| test | news | swarm4 | 156 | 533/542 (98.3%) | 150/156 (96.2%) | 93.2% | 85.3% |

| Domain | Method | Audited | Citation support² | Factual assertions supported | Answers without citations | Gold facts shown | Definition citations | Call citations |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |

### Independent replay of every accepted quote

For each citation, the replay checks its line and character offset in the immutable file and searches the saved model-visible passages for the exact published text. Exterior whitespace is removed as in the original verifier. Raw answers remain in the private transcript archive.

| Phase | Answers | Accepted citations | Exterior whitespace removed | Exact file location | Text delivered | Both verified | Missing exposure archives |
| --- | --- | --- | --- | --- | --- | --- | --- |
| dev | 140 | 456 | 1 | 456 | 456 | 456 | 0 |
| test | 1155 | 3391 | 2 | 3391 | 3391 | 3391 | 0 |
