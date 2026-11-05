# H-17 selected-source compact-state producer test: five original source controls, 3,276,800 complete K04 candidates

**Agent 37 | 5 November 2026 | original archive, read-only.** K01/K02/K03/K05/K06/K07 remain the six independently accepted REC8 components. The original K04 physical coupon and exact Emily K08 margin remain unresolved, so the combined key is **INCOMPLETE**. No original source, verifier, mask, commitment or canonical candidate was modified.

## Recovery hypothesis, distinct from the existing printer-only MT work

The 132 intact printer packets provide substantial conditional MT19937 structure but do not themselves fix the incident-selected physical coupon. Instead, ask whether **independently authenticated, selected source objects in five different archival streams** could have been emitted by one compact-state random stream, with K04 representing a subsequently emitted complete 16-byte block.

This tests a source-authoring relationship rather than altering the disputed 18:02 ACK copy. It is distinct from Agent 9's six fast PRNG fits to *ordinary printer packets*, Agent 35's selected-source GHASH/AES issuer tests, and Agent 46's common Murmur3 x64 native-state inversion. It is nevertheless a **hypothetical common producer**: no company document attests any of the five generators or connects the selected objects to one shared stream. The test uses five real selected 128-bit source objects as controls and also reaches the original K04 digest.

## Original input objects and source verification

The reproducible [single-file Python SFT](../agents/agent37/k04_selected_crossslot_lowstate_sft.py) reconstructs each source object from unchanged records:

| Source object | Genuine retained 16-byte *pre-reduction* block |
|---|---|
| K01: WN-14 signed ink A/B/C/D | `049AAB2E1CDE7A82CD7C60234303C91A` |
| K02: selected eight LT-204 GOOD/HOLD diagnostic words, **before SHA256** | `E1A5E474BAD7E853A2E8C71D3317D507` |
| K05: selected TRP2 node49/event82 CRC-valid latch words | `FF8B78200A56E8586DCDA00EF01E4572` |
| K06: revision C RC-17 four control strips in service order | `5DBF40EE52FAAED9A536D3326CF0D95A` |
| K07: selected AX-7782 transfer checkpoint chain, **before SHA256** | `8947CEDCB9CC73BAB7E87BE63302C5C9` |

Each is independently reduced to its **unchanged original slot SHA256 commitment** before generator work. The spool and transfer evidence SHA256 pins are `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083` and `32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf`. The selected `PS-261003-0417` ACK2 copied payload is **excluded from all state fitting**.

The source objects retain physical prehash bytes wherever possible. K03 is intentionally excluded because its signed serials are variable-length joined text whose accepted K03 component is already a hash of that text, not a physically selected 16-byte prehash object.

## Complete inverse models

1. **Marsaglia xorshift128, 32-bit 11/8/19 recurrence.** Four consecutive full 32-bit outputs determine the entire 128-bit post-block state. Test both word endiannesses, forward/reverse 4-word packet order, every next **8192 consecutive 4-word output window**, and independently all four possible 16-byte K04 serializations.
2. **xoshiro128** 1.1 and 1.0, both 32-bit star-star scramblers. Invert the two odd output multipliers and rotation, then invert a full-rank **128×128 GF(2)** observational system to recover the unique pre-block state from each original source object. Replay the source block exactly. Test the same 8192 future windows and four K04 serializations. Version 1.0 uses the old s[0] scrambler; 1.1 uses corrected s[1], as specified in the [authors' source](https://prng.di.unimi.it/xoshiro128starstar.c).
3. **Reversible SplitMix64 Stafford-13 and Murmur-finalizer variants.** Two consecutive 64-bit outputs, independently seen in four layouts, invert to underlying two states and identify each source block's additive 64-bit step `gamma`. Enumerate 8192 following two-output windows and the four K04 serializations. Independently compare the gamma inferred from each of 20 original source layouts across different source families.

For every predicted 16-byte candidate coupon `P`, the original K04 test is **SHA256(P XOR 8556C8CB6140A7F9A5123AC7571BEE1C) == 930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0**. The full 256-bit digest is compared. No K08 phrase or commitment is used.

## Executed original results

| Model | Source anchor layouts | Complete K04 candidate checks | Original K04 hits | Other selected-source whole-block stream matches |
|---|---:|---:|---:|---:|
| xorshift128 | 20 | 655,360 | 0 | 0 |
| xoshiro128** 1.1 | 20 | 655,360 | 0 | 0 |
| xoshiro128** 1.0 | 20 | 655,360 | 0 | 0 |
| SplitMix64 Stafford-13 | 20 | 655,360 | 0 | 0 |
| SplitMix64 Murmur-finalizer | 20 | 655,360 | 0 | 0 |
| **Total** | **100 anchor views** | **3,276,800** | **0** | **0** |

These are complete *candidate assignments*; distinctness between families and serializers was not established. The two SplitMix tests additionally infer **20 source gammas each**, and in both cases **zero matching gammas across different source families**. This is an index-horizon-independent falsifier for the stronger same-gamma, whole-source common-stream claim.

Constructed positives: a genuine 128-bit xorshift state predicts a 23-step later full block exactly; both xoshiro versions independently recover an entire planted 128-bit state from four output words and predict an independently withheld block 49 steps later; both reversible 64-bit mixers reconstruct planted gamma and later full output correctly. The original run against the local uploaded 46-file archive completed successfully. No live or remote computation is claimed.

## Decision and limits

Five separately accepted historical source blocks **do not fit one common stream within 8192 output windows** under these compact-state models and serializers. Independently, the 3,276,800 generated complete physical-coupon *hypotheses* fail original K04 acceptance. This is a finite exclusion of a newly specified cross-archive producer mechanism, **not** evidence that the original printer or office software used any such generator.

A true common generator could use discontiguous outputs, a larger inter-source gap, independently keyed/reseeded streams, a different packet codec or a different algorithm. The physical selected original may be unrelated to these selected source blocks. None of these negatives recovers an authenticated bit of the K04 original or a word of the K08 final caption.

**Next information-bearing bridge:** acquire or discover a contemporary emitter rule predicting two independently selected intact source objects, or an original authenticated selected ACK2/media witness. Scaling unrelated PRNG families without such a source connection would add little. Preserve all six verified slots and keep K04/K08 null in the canonical candidate until exact commitments pass.

## Clean repository CI verification (5 November, 20:16 UTC)

The committed reproducible SFT ran **SUCCESS** on original repository resources under Python 3.11 in [manual GitHub Actions run 42101828580](https://github.com/FlareZ123/workplace-v2/actions/runs/42101828580), independently from the earlier uploaded-ZIP local test. The run re-derived all five original selected blocks, passed every planted full-state/withheld-future control, and checked the same **3,276,800** full original K04 candidates with zero matches and zero cross-source common-gamma matches. The manual workflow was temporary and may be retired after verification; the test source persists.
