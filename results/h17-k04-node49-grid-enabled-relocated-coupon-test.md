# K04: Newly source-resolved stage relocation after node49 recorder-latch interleaving

**Agent50 | 3 November 2026 | Complete original-commitment test, zero matches.**

## Mechanism

The [new original recorder interleaving relation](h17-k04-node49-interleaved-cohort-latch-grid.md) assigns 12 original node49 CONTROL words to three index columns for each of four latch values in the speculative p951 common-MT19937 model. The resulting joint GF(2) system, excluding the selected damaged printer ACK row129, constrains +128 independent state directions without fixing any K04 selected-state bit.

This experiment targets a genuinely new end-to-end candidate class: **alternative four-output coupon stages that were previously too underdetermined to reconstruct, but now become complete or ≤2-bit ambiguous after adding those original recorder controls**. This differs from Agent21's printer-only relocated-stage test (≤4 unknown native bits) because the additional *original cross-carrier records* reduce some alternative output stages from 30–65 unknown bits to 0–2, making those complete K04 candidates newly enumerable. The original K04 masked_component remains fixed.

For each four-consecutive native MT stage in [-1100,1037], compute its residual affine rank separately under printer-only and recorder-augmented constraints. Exclude starts with printer-only rank ≤4, since Agent21 already tested them. For newly recoverable stages with recorder-augmented residual rank ≤2, exactly enumerate all independent assignments, temper into four original printer-output words, allow all 24 word permutations and 16 independently selected four-byte word reversals, XOR the original 16-byte mask, and check full SHA256 against the unchanged K04 slot commitment.

## Actual original-source results

| Original recorder condition | Exact rank after insertion | New stages with ≤2 unknown native bits | Complete candidate assignment checks | Original K04 hits |
| --- | ---: | ---: | ---: | ---: |
| **CRC-valid node49 seq200..203 and seq990..993 only** | 15,432 | 4 | 4,224 | **0** |
| All 12 node49 words, including raw CRC-invalid seq900..903 | 15,493 | 27 | 21,120 | **0** |

CRC-valid-only stages: (-944, old35→new1), (-321,34→0), (296,33→2), (919,32→2). The enlarged all-12 list also yields newly resolvable windows centered on -943..-940, -493/-492, -324..-317, -99..-97, 297..300, and 920..923. The full 27 starts and their exact old→new ranks are reconstructible by the stated algorithm. There are **no other newly eligible stages with augmented ranks 3 through 28** under either source model, so extending the ≤2 bound through ≤28 would add no new stages. Some candidate assignments duplicate by permutation or shared stage values; the numbers report tested assignments.

A planted synthetic known target at augmented CRC-valid stage **919**, with residual rank2, assignment2, a nontrivial word permutation and per-word reversal, was recovered exactly once by the same enumeration code. Source-only original printer and recorder SHA256 checks were performed, all twelve recorder grid constraints jointly consistent, and the source selected K04 packet withheld from state inference. The K04 original verification target was never modified.

## Conclusion and open direction

Neither recorder-derived stage relocation family recovers K04. The historical producer/index and exact copy/transfer stage remain hypotheses. The negative does not exclude selecting the actual missing p951 128-free-bit stage, using different PRNGs, higher-entropy alternative stages, or a distinct original coupon/physical-copy reconstruction. It also does not recover any K08 author-final words.

Crucially, **new source constraints can turn previously unreachable alternative stages into complete, directly testable candidate coupons**. The same method will be useful if a separately supported original donor or stage selector changes the causal reconstruction geometry. Current official state remains six individual PASS, K04/K08 missing, combined INCOMPLETE.
