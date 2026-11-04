# K04: exhaustive four-word same-byte-lane independent correction

**Agent 19 | 4 November 2026. Actual original SHA-256 commitment: 0 matches across 17,179,869,184 complete candidates.** Six canonical REC8/1 components remain PASS; K04/K08 unresolved; combined INCOMPLETE. The original input, canonical candidate and verifier were never edited.

## Source-grounded hypothesis and prior-art distinction

The selected historical event remains `PS-261003-0417`, `2026-10-03T18:02:00Z`, `ATTEMPT=2 STATE=ACK CLASS=RECOVER DEST=bench`. The recovered copy contains `A9A9DC5731A5E2AE879C47215C2559D5`, but the dispatch ACK does not authenticate the physical coupon. The 16-byte original route XOR mask is `8556C8CB6140A7F9A5123AC7571BEE1C`. The unchanged K04 component SHA-256 commitment is `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`.

A plausible transport fault is one independently damaged byte position within **each of four 32-bit source words, all in the same byte lane**. For each lane `l=0..3`, replace bytes `l,l+4,l+8,l+12` of the selected copied coupon with arbitrary independently chosen byte values, preserve all other copied bytes, XOR the unchanged recorded mask and SHA-256 the complete resulting 16-byte component. This assumption changes exactly four byte *positions* (some chosen bytes may accidentally reproduce their copied values). It provides a constrained 32-bit unknown for each lane, with a fault footprint extending across all four words.

Previous v1 exhaustive studies checked all 13 *contiguous* four-byte windows, all arbitrary replacements in up to three noncontiguous byte positions, and a *shared 32-bit XOR disturbance* applied to all words. The present model has **four independent values across four separated positions**, so those predecessor exclusions do not cover it. No copier diagnostic independently confirms that this specific fault occurred; the hypothesis is exploratory.

## Implementation and controls

The [source-pinned C/OpenSSL SFT](../agents/agent19/k04_four_word_byte_lane_sft.c) reads and SHA-pins three immutable official sources before any search:

- `resources/evidence/print/spool-reconstruction.log`: SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`.
- `resources/evidence/recovery-routing.json`: SHA256 `f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5`.
- `resources/acceptance.json`: SHA256 `681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f`.

A **planted complete four-byte correction**, using arbitrary source bytes `DE AD BE EF` in lane2 and a separate in-memory SHA-256 target, was recovered exactly once by the *same* candidate and hash loop. The original K04 commitment is used unchanged and has no accepted matches in the completed search. Local preliminary control also completed the first 16,777,216 original candidates of lane0/shard0-of-256 with zero matches.

The [manually dispatched 32-job GitHub Actions run](https://github.com/FlareZ123/workplace-v2/actions/runs/41755503136) completed with **success** for every job (32 distinct matrix IDs, all `conclusion=success`, paginated job listing checked). It was pinned to source commit `a76c00c3d9da95b8ce432b384dc44f7356df803c`, before the later dual-burst SFT extension. Each job compiles the SFT, passes its planted positive, and checks precisely `2^29=536,870,912` complete original candidates in one disjoint 32-bit range, returning nonzero if any original match exists. A sampled complete action log explicitly shows original full-range counts and `DONE ... original matches=0`. Exhaustiveness follows from the eight contiguous disjoint ranges per lane and all four lanes.

| Coverage | Full SHA-256 comparisons | Accepted |
| --- | ---: | ---: |
| Lane 0: bytes 0,4,8,12 | 4,294,967,296 | 0 |
| Lane 1: bytes 1,5,9,13 | 4,294,967,296 | 0 |
| Lane 2: bytes 2,6,10,14 | 4,294,967,296 | 0 |
| Lane 3: bytes 3,7,11,15 | 4,294,967,296 | 0 |
| **Total** | **17,179,869,184** | **0** |

A prior 256-job dispatch [was voluntarily cancelled](https://github.com/FlareZ123/workplace-v2/actions/runs/41754759473) to consolidate into 32 longer nonoverlapping jobs. It is **not** included in the successful coverage claim.

## Conclusion and boundary

**Excluded:** a copied-packet corruption in exactly one *common byte lane* of each 32-bit word, with each affected byte arbitrary but every other copied byte retained, under the original route-mask XOR and component hash.

**Unresolved:** any copy mechanism damaging a different configuration of byte positions, multiple bursts, broader physical/header divergence, an alternative original coupon, or a stage-specific producer that does not derive the physical selected coupon from the copied buffer. The original coupon is not authenticated even after excluding this candidate family. The run has recovered **zero historical K04 component bits**. The final normalized K08 caption and all its words remain unknown; REC8 full verification remains INCOMPLETE.

The next distinct high-compute search, explicitly separate from this four-lane footprint, treats the copied leading `A9A9` pair as a possible two-byte corruption marker combined with a second independent two-byte burst. Its original program inputs are no more authenticated than the lane model; a no-hit can only exclude that second finite family.
