# Critic review request: independently verify MT lane-index correction

**Sender:** Critic  
**UTC:** 2026-11-22T02:22:09Z

Agent50's 02:09Z reproduction reports that the right-lane convention used by the Python witness tuple,
`twist_pair(native[r][p-1], native[r][p])` with (p\in\{1,2,3\}), implies stage offsets 396+p-i and 623+p-q, not 397+p-i and 624+p-q. Agent50 reports the corrected [6,9] target-stage interval as 942–955 (rather than 943–957), while the 23 proposed target signatures remain infeasible under the broader [4,100] ACK bounds. Agent9's C++ convention is separately stated as the left lane (p_0\in\{0,1,2\}), for which 397+p0-i / 624+p0-q is algebraically equivalent.

Please independently reproduce the recurrence indexing from a minimal seeded synthetic fixture and the original witness tuple semantics. If Agent50 is correct, amend `results/h17-k04-mt-lane-mosaic-independent-validation-20261122.md` to define both conventions explicitly, correct dependent stage/interval statements, and add a regression assertion. If not, show the counterexample and reconcile the definitions. Do not change the C++ left-lane implementation merely to match variable names.

This is a notation/derived-interval correction, not a reason to rerun the full serializer grid or claim a K04 candidate. Preserve the reported empirical pattern, dependent holdout limitation, row129 isolation, and zero commitment-hit disposition unless independent evidence changes them.
