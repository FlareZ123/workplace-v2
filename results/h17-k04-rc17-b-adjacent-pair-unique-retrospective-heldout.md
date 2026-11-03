# RC-17 B adjacent donor pair: all-footer adjacency uniqueness and retrospective printer leverage

**Agent 4, 3 November 2026 | Original-source conditional p951 model.** Follow-on to [the initial independent footer link](h17-k04-rc17-b-consecutive-mt-footer-bridge.md). Both 16-byte K04 physical coupon and Emily's final K08 caption remain unknown.

## Exact source-only pair uniqueness

Use the unchanged original 132 intact printer rows (exclude disputed selected row129), the speculative published p951 MT19937 stage vector, and the original 12 RC-17 revision B/C/D footer strips. At each stage pair -1100..1039 test every *ordered same-revision* pair of distinct sections, in both little/big byte order and native/tempered generator word view. Require each footer to have >=8 original-printer-fixed output bits, and the pair jointly >=26 such bits, before counting an informative trial. No K04 selected-copy bytes, route mask, slot commitment or verifier enters selection.

| View | Informative ordered pair assignments | Exact source-compatible pairs |
|---|---:|---|
| little native | 33,516 | 0 |
| **little tempered** | **33,336** | **1** |
| big native | 33,516 | 0 |
| big tempered | 33,336 | 0 |
| **All** | **133,704** | **1** |

The unique match is **revision B VERIFY `C130C9BB` at native -186 (32/32 bits)** followed by **revision B PURGE `759E0027` at -185 (26/26 bits)**. It is also the only individually qualifying two-footer match in the original >=14-fixed-bits survey. The matching stage and word view were discovered using the same available 132 printer rows, so no prospective p-value claim follows simply from the 133,704 count. The initial stage selection did not fit the actual RC17 source values.

Source-pinned [single-file pair census](../agents/agent4/k04_rc17_b_pair_adjacency_sft.py), importing the previously established source basis, asserts all four per-view counts and the sole pair. This **rules out additional adjacent pairs at the specified bit thresholds**, not arbitrary separated generator placements or other source encodings.

## Target-oriented informativeness stress test

The extra B evidence has an intelligible influence on two preserved intact printer rows, when those rows are dropped from the printer basis and the original B values are inserted at the **previously discovered** -186/-185 coordinates:

| Entire original printer row withheld | Native index | Printer-only known target bits | With B pair added | Agreement of predicted bits |
|---|---:|---:|---:|---|
| r28 | 209..212 | 26/128 | **84/128** | **84/84** |
| r59 | 435..438 | 0/128 | **64/128** | **64/64** |

Among all **132** possible intact one-packet exclusions, these are the **only two** whose source-predictable bit count increases when the B pair is inserted at the same stages. This is a mathematical leverage diagnosis and a controlled withheld-value comparison, but **the choice of B-stage coordinates was made with both r28 and r59 present**, so the new 122 consistent bits are **retrospective predictions and not a blinded independent confirmation**. An explicit stricter test removing both r28 and r59 **before** scanning for RC17 stage matches finds **zero already source-fixed bits** for each footer at -186/-185, and cannot select the pair on its own. This selection-dependence is important and should accompany citations to the discovery.

The two row indices have a direct recurrence explanation: at i=-186, MT19937 uses output positions i+397=211 (within row28) and i+624=438 (within row59). They are mathematically connected to the proposed B anchor by the generator's 397/624 twist terms. The double-holdout loss of all source-fixed donor bits prevents circularly calling this a prospective whole-packet reconstruction success.

## Recovery implications

The original RC17 B pair remains an unusually sharp source-coincident relationship, suggesting a potential cross-carrier generator or copy object. It **does not identify a source-selected original K04 coupon**, authenticate a historical shared RNG or constrain a single of K04's 128 missing bits. A future independently indexed new carrier near MT future donor positions 1179..1181, 1347/1348 or 1574/1575 could materially change the mathematical recovery path. No such witness was found here. Verified state: six individual PASS; K04/K08 unresolved; combined INCOMPLETE.
