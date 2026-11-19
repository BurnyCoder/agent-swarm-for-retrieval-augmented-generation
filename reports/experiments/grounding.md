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
| test | code | arctic | 10 | 26/33 (78.8%) | 8/10 (80.0%) | — | — |
| test | code | oneshot | 9 | 22/28 (78.6%) | 9/9 (100.0%) | — | — |
| test | code | stock | 10 | 25/38 (65.8%) | 8/10 (80.0%) | — | — |
| test | code | swarm1 | 9 | 20/25 (80.0%) | 6/9 (66.7%) | — | — |
| test | code | swarm4 | 8 | 26/28 (92.9%) | 6/8 (75.0%) | — | — |
| test | news | arctic | 24 | 59/70 (84.3%) | 20/24 (83.3%) | 96.9% | 75.9% |
| test | news | oneshot | 24 | 47/50 (94.0%) | 19/24 (79.2%) | 70.8% | 65.3% |
| test | news | stock | 24 | 58/64 (90.6%) | 19/24 (79.2%) | 83.8% | 83.8% |
| test | news | swarm1 | 24 | 68/70 (97.1%) | 19/24 (79.2%) | 88.2% | 77.9% |
| test | news | swarm4 | 24 | 78/81 (96.3%) | 20/24 (83.3%) | 92.6% | 83.8% |

| Domain | Method | Audited | Citation support² | Factual assertions supported | Answers without citations | Gold facts shown | Definition citations | Call citations |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |

### Independent replay of every accepted quote

For each citation, the replay checks its line and character offset in the immutable file and searches the saved model-visible passages for the exact published text. Exterior whitespace is removed as in the original verifier. Raw answers remain in the private transcript archive.

| Phase | Answers | Accepted citations | Exterior whitespace removed | Exact file location | Text delivered | Both verified | Missing exposure archives |
| --- | --- | --- | --- | --- | --- | --- | --- |
| dev | 140 | 456 | 1 | 456 | 456 | 456 | 0 |
| test | 166 | 429 | 0 | 429 | 429 | 429 | 0 |
