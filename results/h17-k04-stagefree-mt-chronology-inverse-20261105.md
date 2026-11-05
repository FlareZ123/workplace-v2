# K04: source-blind stage-free MT19937 chronology inverse

**Agent 5 | 5 November 2026. Historical K04 remains unresolved.**

## The new reconstruction question

The [previous unindexed MT printer fingerprint](h17-k04-source-unindexed-mt-twist-fingerprint-20261105.md) finds 25 exact fullword twist relations before any native generator stages are supplied. Instead of assuming the inherited p951 absolute stage map, invert **only these original numerical equations** to reconstruct stage differences. The retained 18:02 ACK2 selected payload, K04 masked component, acceptance SHA, and Agent49's STARTS list are deliberately excluded from the research inputs.

Use an integer weighted union-find for the exact recurrence displacements: relative source stages for relation operands are 1, 397, and 624 draws apart. Packets contain four consecutive native outputs. Add historical event-order inequalities requiring at least four draws between consecutive rows and a placeholder for the selected unknown row129. Exact longest-path difference constraints give lower and upper bounds on its possible stage.

Original printer spool source SHA256: `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`.

## Measured original source information

| Observation | Result |
| --- | ---: |
| Independently rediscovered exact twist links | 25 |
| Intact printer rows / connected equality components | 132 / 96 |
| Non-singleton components / packets in them | 14 / 50 |
| Largest components | four size-5, ten size-3 |
| Independent packet-start equalities | 36 |
| Selected draw offset after prior row128 | **4..59** |
| Draw offset from selected to next row130 | **4..59** |
| Full native words uniquely fixed relative to selected | **0** |
| Complete selected words predicted | **0 of 4** |
| Authenticated historical coupon bits | **0 of 128** |

The 56 possible integer offsets between row128 and the selected row are jointly constrained by chronology, yet do not identify the event stage. The selected row is not connected by any of the exact equalities, and no other original native word has a unique relative stage against it under these constraints.

In ten **blind whole-packet holdouts** (row IDs 10, 21, 34, 53, 73, 83, 101, 117, 128 and 130), the source relations and graph were rediscovered with the whole target packet removed. All ten have ambiguous stages and zero predicted complete native words. This is a test of whole-packet predictive ability, not a K04 hash sweep.

A separate *genuine* seeded MT synthetic positive at seed 90210 with 255 of 256 consecutive packets retained has 297 discovered links. Its stage graph uniquely locates 1,020 native source words and reconstructs **all four** genuinely withheld words (stages 800..803) exactly. A second seeded nonuniform MT sequence has 36 correct links. In 32 seeded chronological packet shuffles of the unchanged original values, discovered link counts range 1..11, mean 5.15625; five shuffled graphs remain chronologically feasible.

## Reproducer and limits

[Single runnable source-pinned Python file](../agents/agent5/k04_unindexed_stage_inverse_graph_sft.py) implements source parsing, native untempering, independent relation discovery, graph constraints, ten holdouts, fully recovered synthetic packet positive and chronology shuffles. Executed source-equivalent locally against the uploaded original archive; committed implementation was byte-for-byte read back.

The 4..59 bounds assume one common native MT generator, four outputs consumed per logged packet, and no chronology reversal. These assumptions remain unverified physical history. The new result exposes the **unfixed stage and missing native source information** before any original acceptance attempt; it cannot authenticate the printer coupon or infer a genuine K08 final-caption word.

**Official REC8:** K01/K02/K03/K05/K06/K07 PASS, K04 and K08 MISSING, combined INCOMPLETE.
