# Index setup and loading

Setup time includes opening an immutable corpus, constructing or loading a search index and initializing the local encoder when required. Concurrent loaders can wait on a shared build. These times are excluded from per-question latency.

| Corpus or snapshot | Mode | Spans | Seconds | UTC |
| --- | --- | --- | --- | --- |
| 3cfa40b121d2 | arctic | — | 4.867 | 2026-11-19T14:15:00.014+00:00 |
| a591f53b8ba3 | arctic | — | 10.178 | 2026-11-19T13:37:23.246+00:00 |
| aa3807318c8b | arctic | — | 10.12 | 2026-11-19T14:12:58.509+00:00 |
| de731153f2b6 | arctic | — | 12.324 | 2026-11-19T14:17:07.934+00:00 |
| django | hybrid | 31434 | 24.635 | 2026-11-19T14:18:16.607+00:00 |
| django | lexical | 31434 | 21.195 | 2026-11-19T14:18:22.384+00:00 |
| flask | hybrid | 1237 | 1.293 | 2026-11-19T14:12:46.139+00:00 |
| flask | lexical | 1237 | 0.286 | 2026-11-19T14:12:47.473+00:00 |
| news | hybrid | 6220 | 59.851 | 2026-11-19T13:41:45.135+00:00 |
| news | hybrid | 6220 | 137.243 | 2026-11-19T13:50:02.361+00:00 |
| news | lexical | 6220 | 1.036 | 2026-11-19T13:37:13.048+00:00 |
| news | lexical | 6220 | 4.156 | 2026-11-19T13:39:28.174+00:00 |
| news | lexical | 6220 | 1.022 | 2026-11-19T13:53:09.835+00:00 |
| pytest | hybrid | 5315 | 3.097 | 2026-11-19T14:15:52.104+00:00 |
| pytest | lexical | 5315 | 0.731 | 2026-11-19T14:16:26.770+00:00 |
| requests | hybrid | 1243 | 0.571 | 2026-11-19T14:13:50.583+00:00 |
| requests | lexical | 1243 | 0.236 | 2026-11-19T14:14:55.127+00:00 |
