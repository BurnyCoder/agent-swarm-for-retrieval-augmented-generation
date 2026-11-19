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
| test | code | arctic | 79 | 237/295 (80.3%) | 77/79 (97.5%) | — | — |
| test | code | oneshot | 81 | 173/222 (77.9%) | 80/81 (98.8%) | — | — |
| test | code | stock | 80 | 306/345 (88.7%) | 78/80 (97.5%) | — | — |
| test | code | swarm1 | 81 | 305/323 (94.4%) | 78/81 (96.3%) | — | — |
| test | code | swarm4 | 79 | 331/343 (96.5%) | 77/79 (97.5%) | — | — |
| test | news | arctic | 166 | 427/481 (88.8%) | 148/166 (89.2%) | 95.7% | 78.2% |
| test | news | oneshot | 166 | 327/349 (93.7%) | 147/166 (88.6%) | 71.0% | 61.8% |
| test | news | stock | 166 | 455/509 (89.4%) | 161/166 (97.0%) | 82.6% | 82.6% |
| test | news | swarm1 | 165 | 472/501 (94.2%) | 151/165 (91.5%) | 89.6% | 78.0% |
| test | news | swarm4 | 165 | 561/572 (98.1%) | 159/165 (96.4%) | 93.6% | 86.0% |

| Domain | Method | Audited | Citation support² | Factual assertions supported | Answers without citations | Gold facts shown | Definition citations | Call citations |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |

### Independent replay of every accepted quote

For each citation, the replay checks its line and character offset in the immutable file and searches the saved model-visible passages for the exact published text. Exterior whitespace is removed as in the original verifier. Raw answers remain in the private transcript archive.

| Phase | Answers | Accepted citations | Exterior whitespace removed | Exact file location | Text delivered | Both verified | Missing exposure archives |
| --- | --- | --- | --- | --- | --- | --- | --- |
| dev | 140 | 456 | 1 | 456 | 456 | 456 | 0 |
| test | 1228 | 3594 | 2 | 3594 | 3594 | 3594 | 0 |
