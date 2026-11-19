# Index setup and loading

Setup time includes opening an immutable corpus, constructing or loading a search index and initializing the local encoder when required. Concurrent loaders can wait on a shared build. These times are excluded from per-question latency.

| Corpus or snapshot | Mode | Spans | Seconds | UTC |
| --- | --- | --- | --- | --- |
| a591f53b8ba3 | arctic | — | 10.178 | 2026-11-19T13:37:23.246+00:00 |
| news | hybrid | 6220 | 59.851 | 2026-11-19T13:41:45.135+00:00 |
| news | hybrid | 6220 | 137.243 | 2026-11-19T13:50:02.361+00:00 |
| news | lexical | 6220 | 1.036 | 2026-11-19T13:37:13.048+00:00 |
| news | lexical | 6220 | 4.156 | 2026-11-19T13:39:28.174+00:00 |
| news | lexical | 6220 | 1.022 | 2026-11-19T13:53:09.835+00:00 |
