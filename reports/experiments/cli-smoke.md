# Normal Windows CLI checks

Both checks use the same two-file fixture. The positive question requires combining a route choice with a stop count. The missing-date question tests abstention. These checks establish end-to-end behavior on one fixture.

| Question | Expected | Observed | Agents | Investigators completed | Verified quotes | Seconds | USD upper |
| --- | --- | --- | --- | --- | --- | --- | --- |
| How many stops are on the schedule followed by the Brook service? Give the integer. | 41 | 41 | 4 | 3 | 2 | 34.33 | 0.006273111 |
| In which four-digit year did the Brook service open? If the files give no date, answer Insufficient information. | Insufficient information | Insufficient information | 2 | 1 | 2 | 30.666 | 0.003014911 |
