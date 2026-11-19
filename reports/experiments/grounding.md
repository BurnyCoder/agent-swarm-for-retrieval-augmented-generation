# Source grounding

¹ Mean per-question recall on questions with annotated files. Returned-file recall depends on path visibility in each tool interface. ² Citation support includes one failed opportunity for each answer without citations. Exact quote matching, assertion support, and annotated fact exposure have different denominators.

| Phase | Domain | Method | Answers | Literal quotes valid | Answers with citations | Gold files returned¹ | Gold files cited¹ |
| --- | --- | --- | --- | --- | --- | --- | --- |
| dev | news | arctic | 1 | 3/3 (100.0%) | 1/1 (100.0%) | 100.0% | 100.0% |
| dev | news | oneshot | 2 | 3/3 (100.0%) | 1/2 (50.0%) | 100.0% | 100.0% |
| dev | news | stock | 1 | 3/3 (100.0%) | 1/1 (100.0%) | 100.0% | 100.0% |
| dev | news | swarm1 | 2 | 4/4 (100.0%) | 2/2 (100.0%) | 100.0% | 100.0% |

| Domain | Method | Audited | Citation support² | Factual assertions supported | Answers without citations | Gold facts shown | Definition citations | Call citations |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
