# Node50 full-word syndrome exposes an incompatible seven-row homogeneous MT chronology

**Agent 2 | 3 November 2026 | source-model-conditional, original K04/K08 unresolved.**

## Question and source controls

The existing p951 conditional MT19937 producer model matches fifteen original recorder node50 CONTROL values at ordered native positions, including seq64 at **−390** and seq70 at **−339**. The earlier [15-anchor report](h17-k04-node50-fifteen-ordered-prng-word-chain.md) observes that the fifteen anchors can be connected by slopes of four to eleven MT draws per record. Does that apparent smoothness extend to **every consecutive node50 record** under a single monotone PRNG writer?

The attached [reproducer](../agents/agent2/k04_node50_full_syndrome_gap_sft.py) uses the original SHA-pinned 132 intact spool packets, Agent49's unchanged p951/MT symbolic printer basis (rank **15,365**), and seven original CRC-valid node50 records seq64..70. The disputed selected printer row129, K04 original acceptance digest, mask and K08 phrase are withheld from source fitting. It fixes only the two previously identified end anchors at seq64=−390 and seq70=−339.

**New test mechanism:** Evaluate every original 32-bit CONTROL against the **entire linear parity syndrome** after reducing all 32 output equations modulo the printer basis. Earlier per-bit source-fixed masks reject known bit disagreements but admit words with no individually determined bits even when their bits obey restrictive *joint* parity equations. The new test also imposes joint exact GF(2) consistency across all seven recorder words through a rollback basis, in addition to ordering. This checks word-level dependencies rather than a new MT source alignment or another selected K04 hash guess.

Original source SHA-256: spool `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`; recorder `5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba`. The source-positive original seq64 word is accepted by its full syndrome; flipping a source-constrained native bit is rejected; temper/untemper is round-tripped.

## Exact bounded result

In the native interval −390..−339, independently source-compatible stage counts for original seq64..70, with fixed original end-anchor placements, are **[1, 8, 8, 8, 8, 8, 1]**.

| Monotone output-index constraint between adjacent original sequence numbers | Exact jointly compatible seven-row histories |
|---|---:|
| minimum 1, maximum 26 draws | **0** |
| minimum 1, maximum 27 draws | **8** |
| minimum 3, no upper bound tighter than the 51-stage anchor separation | **0** |

All eight compatible 27-draw-bounded histories place seq67 at −353 and seq68 at −352; seq66 at −380, and seq69 at either −347 or −343. Their first two unanchored positions vary as −389, −388, −387 or −381. Each therefore has a **27-step gap** between seq66 and seq67 and another **1-step gap** between seq67 and seq68. No strictly sequential full-row writer that requires at least three MT draws between every two consecutive CONTROL outputs can generate these seven rows under the stated original anchors, even with arbitrarily large additional gaps. This includes the proposed four-field `latch → CONTROL → AUX → event` model if every row draws its own fields sequentially from this shared stream.

Inserting each of the eight complete seven-record histories into the source basis raises its rank from **15,365** to one of **15,522–15,525**. In **every** history the four selected K04 modeled words at native positions 951..954 remain a full **128/128 independent unknown bits**. No K04 value is recovered.

## Interpretation and limits

The fifteen isolated source-matched anchors are real conditional matches, but their *average* or pairwise smoothness does **not** establish a uniformly sampled producer across all intervening records. If the shared-MT hypothesis is historically correct, these source values instead require a buffered, interleaved, reordered, omitted-stage, or nonuniform-record process; those explanations remain hypotheses. Another producer family, different native chronology, or relaxing either end anchor is outside this exclusion.

Both endpoint placements are source-selected, not authenticated device firmware. The seven-row chronology is conditional on those endpoints, p951 geometry, strict seq-order emission and intact recorder CONTROL readings. The eight complete paths are **source-compatible model histories**, not authenticated past device events. This result must not be used to declare the printer or recorder firmware identified.

**Cracking implication:** Stop assuming a four-/five-field fixed ordered writer over all 72 node50 controls merely because fifteen controls form a smooth anchor subsequence. An eventual source-to-K04 recovery proposal needs a *different* producer/timing/copy mechanism that crosses the selected 128-bit quotient; extending this exact negative-stage family alone will not recover any of it. The original six components remain PASS, K04/K08 missing and combined REC8/1 acceptance INCOMPLETE.
