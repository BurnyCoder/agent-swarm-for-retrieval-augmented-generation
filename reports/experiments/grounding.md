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
| test | code | arctic | 81 | 246/304 (80.9%) | 79/81 (97.5%) | — | — |
| test | code | oneshot | 81 | 173/222 (77.9%) | 80/81 (98.8%) | — | — |
| test | code | stock | 81 | 311/350 (88.9%) | 79/81 (97.5%) | — | — |
| test | code | swarm1 | 81 | 305/323 (94.4%) | 78/81 (96.3%) | — | — |
| test | code | swarm4 | 81 | 340/352 (96.6%) | 79/81 (97.5%) | — | — |
| test | news | arctic | 169 | 434/490 (88.6%) | 151/169 (89.3%) | 95.5% | 78.1% |
| test | news | oneshot | 169 | 331/353 (93.8%) | 150/169 (88.8%) | 70.2% | 61.2% |
| test | news | stock | 169 | 462/517 (89.4%) | 164/169 (97.0%) | 82.1% | 82.1% |
| test | news | swarm1 | 169 | 487/516 (94.4%) | 155/169 (91.7%) | 89.4% | 78.1% |
| test | news | swarm4 | 169 | 577/588 (98.1%) | 163/169 (96.4%) | 93.4% | 85.8% |

| Domain | Method | Audited | Citation support² | Factual assertions supported | Answers without citations | Gold facts shown | Definition citations | Call citations |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |

### Independent replay of every accepted quote

For each citation, the replay checks its line and character offset in the immutable file and searches the saved model-visible passages for the exact published text. Exterior whitespace is removed as in the original verifier. Raw answers remain in the private transcript archive.

| Phase | Answers | Accepted citations | Exterior whitespace removed | Exact file location | Text delivered | Both verified | Missing exposure archives |
| --- | --- | --- | --- | --- | --- | --- | --- |
| dev | 140 | 456 | 1 | 456 | 456 | 456 | 0 |
| test | 1250 | 3666 | 2 | 3666 | 3666 | 3666 | 0 |
