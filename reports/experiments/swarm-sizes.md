# Swarm size and participation

The frozen development choice is **4 agents**, including the coordinator. The cost rule admitted **10 balanced blocks**. An investigator contributes when at least one of its source quotations passes validation. Peak concurrency counts overlapping investigator session lifetimes.

| Phase | Domain | Size condition | Cases | Investigators assigned | Returned | Supplied verified evidence | Max simultaneous | Repeated span reads | Mean requests | Mean output tokens |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| dev | code | swarm1 | 10 | 0 | 0 | 0 | 0 | 0 | 4.3 | 2174 |
| dev | code | swarm2 | 10 | 10 | 10 | 10 | 1 | 0 | 7.1 | 3760 |
| dev | code | swarm4 | 10 | 30 | 30 | 29 | 3 | 86 | 15.2 | 7922 |
| dev | code | swarm8 | 10 | 70 | 70 | 62 | 7 | 9 | 19.1 | 11797 |
| dev | news | swarm1 | 10 | 0 | 0 | 0 | 0 | 0 | 5.7 | 2473 |
| dev | news | swarm2 | 10 | 10 | 10 | 10 | 1 | 0 | 8.6 | 3940 |
| dev | news | swarm4 | 10 | 30 | 30 | 29 | 3 | 101 | 16.7 | 7520 |
| dev | news | swarm8 | 10 | 70 | 70 | 65 | 7 | 36 | 20.0 | 10468 |
| test | code | swarm1 | 74 | 0 | 0 | 0 | 0 | 0 | 5.3 | 2375 |
| test | code | swarm4 | 74 | 222 | 214 | 208 | 3 | 394 | 15.5 | 7886 |
| test | news | swarm1 | 156 | 0 | 0 | 0 | 0 | 0 | 5.1 | 2273 |
| test | news | swarm4 | 156 | 468 | 453 | 428 | 3 | 1718 | 15.6 | 7118 |

### First held-out block

| Domain | Condition | Pairs | Quality | Difference from swarm1 [95%] | USD / question | Median seconds |
| --- | --- | --- | --- | --- | --- | --- |
| code | swarm1 | 15 | 59.13 | +0.00 [+0.00, +0.00] | 0.0059 | 69.4 |
| code | swarm4 | 15 | 67.47 | +8.33 [-0.93, +21.20] | 0.0209 | 145.5 |
| news | swarm1 | 32 | 46.88 | +0.00 [+0.00, +0.00] | 0.0054 | 59.0 |
| news | swarm4 | 32 | 53.12 | +6.25 [-9.38, +21.88] | 0.0191 | 115.4 |
