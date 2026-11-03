# New export-permutation side channel (3 November 2026, Agent 3)

The original TRP2 recorder has 88 shuffled rows, transfer audit 68 rows, and telemetry 145 retrieval-order rows. A new possible K04 information carrier is the permutation itself: if the files were shuffled using the **same** MT19937 producer as the printer packets, Fisher-Yates swap indices may constrain otherwise unobserved producer state.

**Method.** Reuse the conditional p951 printer-only source model: original spool SHA `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`, 132 intact printer packets excluding disputed row129, GF(2) rank 15,365. Project the top eight tempered MT output bits at every proposed index -1100..1040, marking unconstrained bits unknown. Invert the observed file permutation for each candidate original sequence-order layout to get the exact accepted Fisher-Yates swaps. A backward DP then tests whether any CPython `random.shuffle` sequence fits those accepted swaps, permitting an **arbitrary number of rejected `getrandbits(k)` draws** before each accepted swap. State beyond 1040 is treated as wholly unknown, so near-boundary positives are not source-established.

Layouts: **48** recorder cases (node50 seq0..71 followed or preceded by the four node49 four-record cohorts in all 24 cohort permutations), **96** transfer cases (all 24 AX group orders, seq-vs-attempt ordering, receipts before/after each group), and **7** telemetry cases (sequence, time, tag and DIAG/PV block orderings). These are candidate row-generation orders, not historical assertions.

| Original export | Tested layouts | Any compatible start | Total compatible starts |
|---|---:|---:|---:|
| Recorder (88) | 48 | 0 | 0 |
| Transfer audit (68) | 96 | 18 | 90 |
| Telemetry (145) | 7 | 0 | 0 |

All 90 transfer survivors occur at **MT starts 1034..1039**, immediately before the unconstrained right boundary. **No layout in any file survives for a start ≤1033**. A planted synthetic Python `random.shuffle` with 150 preceding `getrandbits(32)` draws was recovered at its exact start, validating the inverse and rejection-state mechanics.

**Inference.** A shared-source, CPython-shuffle architecture with these original record-creation layouts is excluded inside the nonboundary portion of the p951 horizon. This does **not** exclude independent shuffle seeds, different initial ordering, another printer geometry, a later index, a stage reset, a non-CPython shuffle or an actual historical correlation that needs a different mapping. The printer p951 model remains conditional and the shuffles supply **zero authenticated K04 bits**. K08 exact words remain unknown.

**Reproducer:** [single-file test](../agents/agent3/k04_export_shuffle_p951_sft.py), run `python agents/agent3/k04_export_shuffle_p951_sft.py resources`. It pins the source file hashes and does not use K04/K08 commitments or the selected ACK to fit its model.

**New direction:** file order is a distinct candidate source channel; pursue an independently anchored writer/seed reset or row-creation order if such a witness emerges, rather than automatically relabeling observed UTC time as PRNG generation time. The REC8 verifier remains six PASS, combined INCOMPLETE.
