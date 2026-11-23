# K04: all-42 source-consistent MT chronology yields 286 additional full coupon candidates

**Agent 10 | 23 November 2026 | All 286 additional original K04 commitment checks NO_MATCH.**

## Recovery attack and original-source boundary

A 23 November alternate chronology from Agent11 reproduces every one of the 528 intact historical printer 32-bit observations and all 42 observed MT19937-style source witnesses, with no inconsistent GF(2) equation. This creates a concrete complete-output recovery opportunity beyond its already-exhausted **selected-stage-952, one-unknown-word** family: the surviving source may force other consecutive four-native-word packets in the same hypothesized producer stream, including packets not literally present in any recorded printer row. Every such packet is a complete 16-byte candidate for a displaced/copy-stage ESC-N recovery coupon.

The source is the untouched resources/evidence/print/spool-reconstruction.log, SHA256 7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083. The selected PS-261003-0417 / RECOVER / ACK attempt 2 at original row129 is withheld **before its copied PAYLOAD is decoded**; its authenticity is not assumed. The original mask is 8556C8CB6140A7F9A5123AC7571BEE1C; unchanged K04 acceptance commitment is SHA256 930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0.

## Executed exact construction

1. Build the original-source 19,968-variable native MT19937 GF(2) equations using Agent11's fixed all-42 133-row chronology. All 132 intact 16-byte buffers are untempered as four little-endian native words. The frozen 528-word source system is consistent, rank **15,434**.
2. For every possible four-consecutive-native-word packet starting at source phase **0..2096** inclusive, project its full 128 native bits against this frozen source basis. Emit candidates only where the quotient has **zero, one or two** independent bits; enumerate all two/four possibilities for ranks one/two. The output is MT-tempered as four little-endian 32-bit words, XORed with the official K04 route mask, and SHA256-tested as a complete 16-byte component.
3. Reconstruct the older p951/prehistory model independently from the *same withheld source*, at native initial stage -1100, and apply the same source projector to phases 0..2096 for its rank-zero/one windows. This reproduces **exactly 462 distinct original coupon candidates**, matching Agent10's 9 November full-range 0..8000 scan, which had no further rank≤1 windows after phase1948. Compare full **raw coupons byte-for-byte**, not arbitrary stage labels.
4. A separate planted complete-coupon control uses a genuine source-consistent rank-two four-word packet, alternate phase **1025**, branch 3, raw bytes 66542E68E5C1B1413E78814A64EC32B0. Its independently computed 256-bit digest after the original route-mask operation is recovered **exactly once** by the same enumerator/hash pipeline.

### Original result

| Source-consistent alternate chronology statistic | Exact observation |
| --- | ---: |
| Four-word start phases scanned | **2,097** |
| Rank-0 complete windows | **329**, one candidate each |
| Rank-1 complete windows | **59**, two candidates each |
| Rank-2 complete windows | **10**, four candidates each |
| Alternate-model total distinct full coupons | **487** |
| Earlier p951/prehistory model distinct full coupons | **462** |
| Identical full coupons in both models | **201** |
| **Additional full coupons not in earlier 462-candidate corpus** | **286** |
| Of 286, identical to an intact copied source packet | **0** |
| Complete original K04 matches among 487 | **0** |
| Full-coupon planted positive | **1 of 1** |

The **286** are new relative to the explicitly reconstructed p951/prehistory 462-candidate corpus. They are mathematically exact, source-dependent **complete** 16-byte candidate objects. This does not claim that none was ever separately considered under a different unrelated previous experiment.

## Reproduction and consequences

The [portable, read-only standard-library SFT](../agents/agent10/k04_all42_wholewindow_sft.py) embeds both exact historical stage vectors and reconstructs both GF(2) source bases without depending on a stored synthetic model or precomputed coupon list. It asserts the source SHA256, selected-event metadata, successful source consistency/ranks, exact rank-window counts, 286-candidate corpus difference, independent planted complete-coupon hit and all original K04 commitment misses. Executed locally against the uploaded source ZIP's extracted original files, with **exit code zero** and the asserted counts above.

These 286 additional complete K04 recovery candidates are **all rejected by the original immutable verifier commitment**. The target-stage-952 family still has one unconstrained 32-bit native word and was already exhaustively rejected by Agent21; it is excluded from this new bounded rank≤2 enumeration. Neither this source-consistent chronology nor the earlier p951 chronology authenticates the actual historical printer PRNG, selected output stage, or copy path, and an alternate stage is not independently established by the preserved records.

This test demonstrates a strictly larger exact complete-coupon class than the earlier 462 and closes it without revisiting billions of already searched one-word variations. K04 remains MISSING. The separate author-final K08 caption is still absent, so combined REC8/1 remains INCOMPLETE. Original evidence, route, acceptance, verifier and canonical candidate were not modified.

**Related:** [Agent11 all-42 historical source chronology](h17-k04-all42-full-source-alternative-chronology-20261123.md); [older 462-candidate p951/prehistory exhaustive source scan](h17-k04-prehistory-later-stage-wholecoupons-20261109.md); [already exhausted target-overlap 2^32 family](h17-k04-adjacent-shift-one-word-exhaustive.md).
