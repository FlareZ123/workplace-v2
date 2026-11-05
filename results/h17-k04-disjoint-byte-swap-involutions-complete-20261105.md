# K04: complete disjoint-pair byte-swap copying fault family

**Agent 13 | 5 November 2026 | 46,206,736 complete original candidate assignments, original K04 NO_MATCH.** Original six slots remain individually PASS; K04 and K08 missing; combined REC8 INCOMPLETE.

## Why a source-specific new fault geometry

The actual selected printer spool event is ESC-N / PS-261003-0417 / 18:02 UTC / attempt2 RECOVER ACK. Its **unverified copied** 16-byte buffer is `A9A9DC5731A5E2AE879C47215C2559D5`. Source MAIL16 and custodian note explicitly distinguish dispatch ACK from physical coupon integrity. A copy assembler with swapped byte-address pairs could create a physical coupon containing exactly those 16 copied byte values but in different positions; one such error could affect more than four positions.

This model permits **any involutive permutation of the 16 byte positions**: each position is either fixed or paired in a transposition with one other position; transposition pairs are disjoint. Thus we enumerate arbitrary independent pair swaps across 32-bit word boundaries, up to eight simultaneous swaps changing as many as 16 positions. Previous 24^5 lane-permutation search was limited to four permuted bytes within each fourword plus whole-word reorder; the exhaustive <=4 changed-byte support search covers at most two disjoint value-changing swaps. This model has an additional, previously uncovered **three-or-more disjoint cross-word swap family**, with no arbitrary value replacement.

The physical copier fault is **hypothetical**. The surviving source does not authenticate any such reordering or prove that the physical original preserved the same byte multiset.

## Exact complete space and source-gated method

Involutions on 16 labeled positions have `sum_{k=0}^{8} 16!/(2^k k! (16-2k)!) = 46,206,736` assignments. The selected copied coupon has duplicated `A9`, so distinct permutation assignments can coincide in candidate coupon bytes; counts below are **assignments, not necessarily distinct component values**.

The recursive source-pinned [C++17/OpenSSL SFT](../agents/agent13/k04_allbyte_involutions_sft.cpp), using the directly included [complete-permutation source/reducer SFT](../agents/agent13/k04_allbyte_permutation_sft.cpp), fixes the smallest unassigned position or pairs it with each higher remaining position. Every involutive position map is visited once, including up to eight swaps, with no unordered-pair duplication. For each full reconstructed physical 16byte candidate, XOR original source `8556C8CB6140A7F9A5123AC7571BEE1C` and compare SHA256 of the resulting **complete component** with the untouched K04 digest `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`.

The same code validates unaltered original spool SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`, route SHA256 `f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5`, acceptance SHA256 `681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f`, and uniquely reselects the original event. One-block SHA256 against canonical OpenSSL SHA256 is self-checked on seven distinct original-source permutation ranks before enumeration.

## Complete executed local result

| Simultaneous disjoint swaps | Complete position-map assignments | Original K04 matches | Planted positives |
| ---: | ---: | ---: | ---: |
| 0 | 1 | 0 | 0 |
| 1 | 120 | 0 | 0 |
| 2 | 5,460 | 0 | 0 |
| 3 | 120,120 | 0 | 0 |
| 4 | 1,351,350 | 0 | 0 |
| 5 | 7,567,560 | 0 | 0 |
| 6 | 18,918,900 | 0 | **1** |
| 7 | 16,216,200 | 0 | 0 |
| 8 | 2,027,025 | 0 | 0 |
| **Total** | **46,206,736** | **0** | **1** |

An independently chosen synthetic complete coupon from six **cross-word** swap pairs `(0,7),(1,11),(2,9),(3,13),(4,15),(5,8)` was hashed through exactly the same original mask and full SHA256 commitment path, and the enumerator returned that planted coupon once. The original scan and all nine combinatorial counts were asserted in the SFT. The original read-only extracted archive ran locally with g++ C++17 `-O3` and OpenSSL in about **3.08 seconds**.

## Status and relation to larger in-flight search

**Source-conditioned exhaustive negative for byte-address *involutions only*.** This eliminates any physical original that differs from the copied selected packet only by a disjoint set of arbitrary transpositions of its byte positions. A general arbitrary permutation can contain cycles longer than two; those are outside this completed 46.2million assignment test.

A separate **unrestricted 16byte byte-multiset permutation** test, subsuming this family, was independently launched with 256 disjoint GitHub Actions shards and its source-pinned 10million-candidate pilot passed. That [larger run](https://github.com/FlareZ123/workplace-v2/actions/runs/41965620442) was still **queued** when this report was authored; the full 10.46trillion negative is **not** claimed. The distinction avoids crediting in-flight work as completed.

This result does not authenticate a physical coupon byte, and cannot rule out value substitutions, loss of entire source copy, a different original producer, or correct bytes hidden in another medium. K08 exact terminal words remain wholly unobserved.
