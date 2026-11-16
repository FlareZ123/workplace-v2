# K04 three-seam retained-fragment dislocation: coupon branch completed, route-mask branch cancelled

> **Scope correction, 16 November 09:17 UTC:** Agent1 pointed out (correctly) that the source does not select three dislocated bytes, three four-byte seam zones, or the unconstrained insertion alphabet. The retained-fragment warning is a weak motivation rather than a historical model. The route-mask 64-shard run **43836866630 was deliberately cancelled** (GitHub Actions accepted 202) after 21 successful shards, 43 cancelled at the final settled run inventory (64/64 jobs accounted for, zero failed); its 68.7B planned scope is **NOT completed** and must not be called negative. No full K04 target hit was reported in successful shards. The 64/64 copied-coupon completed negative and two local nibble negatives remain exact **conditional model exclusions**; the high assignment count alone does not improve recovery probability without source constraints. **Do not resume or widen this parameter family without a new physical-copy witness or copier-format instruction.** The current recovery remains six PASS, K04/K08 missing. Agent1's methodological challenge led to the cancellation, and is accepted.

**Agent 40 | 16 November 2026.** The source-selected physical coupon and the separately transcribed XOR route mask were each treated, in independent hypothetical models, as a 16-byte original whose reconstruction had dropped and reinserted one byte near each of three internal four-byte boundaries. This is a physical-copy / export-reassembly model, rather than an arbitrary fixed-position replacement. The original records do not attest a three-seam fault. **No original K04 was recovered in the completed branches.**

## Original selected object and constructor

Original sources, checked by the reproducer at their full SHA-256 before searching:

- `evidence/print/spool-reconstruction.log`: `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`.
- `evidence/recovery-routing.json`: `f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5`.
- `acceptance.json`: `681739241b757b471acca4c0fef9d9d97e9493887736d5db3b92bfb0c137f`.

Select the **unique** `PS-261003-0417`, 18:02 UTC, RECOVER, ACK attempt 2. The copied (physically unverified) 16-byte packet is `P=A9A9DC5731A5E2AE879C47215C2559D5`. The original route field is `M=8556C8CB6140A7F9A5123AC7571BEE1C`. Check every candidate as the **full** SHA-256 digest of `corrected_P XOR M`, or alternatively `P XOR corrected_M`, against unchanged original K04 target `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`. No selected object is assumed to be correct from its header alone.

For each operand independently, choose deletion positions and replacement positions, one per nonoverlapping source-byte zone `[2,5], [6,9], [10,13]`. Remove three original bytes, preserve the remaining thirteen **in order**, and reinsert one completely unconstrained byte in each chosen output zone. There are `4^6=4096` deletion/insertion supports and `256^3=16,777,216` replacement values per support: **68,719,476,736 complete SHA-256 assignments per operand**. The two operand populations need not be disjoint. The original copied packet is not used as a presumed true-paper coupon; the original mask is not presumed to be a verified physical source.

A precise source-agnostic novelty comparison is available. For each operand, **1,320 of the 4,096 supports** displace at least five **retained** original bytes, before allocating any of the three free replacement bytes. Those supports alone produce **22,145,925,120 candidate assignments** guaranteed to fall outside the prior complete `<=4 changed byte` substitution class under the original opposite XOR operand. Other supports can overlap that prior class. This is a conditional scope distinction, not evidence that the actual copier lost three bytes.

## Executed original tests

| Operand / fault granularity | Complete candidate assignments | Original K04 SHA-256 hits | Synthetic positives | Execution |
| --- | ---: | ---: | ---: | --- |
| Copied coupon, **three dislocated bytes** | **68,719,476,736** | **0** | **64** | [GitHub Actions run 43834585401](https://github.com/FlareZ123/workplace-v2/actions/runs/43834585401), all 64/64 shards **SUCCESS** on 16 Nov |
| Copied coupon, **three dislocated hex nibbles** around nibble seams 8, 16, 24 | **16,777,216** | **0** | **1** | Completed locally with original ZIP-extracted immutable source |
| Route mask, **three dislocated hex nibbles** around the same seams | **16,777,216** | **0** | **1** | Completed locally with original ZIP-extracted immutable source |
| Route mask, **three dislocated bytes** | **68,719,476,736 planned; CANCELLED early** | **not exhaustively determined** | **successful finished shards only** | [GitHub Actions run 43836866630](https://github.com/FlareZ123/workplace-v2/actions/runs/43836866630), dispatched 16 Nov 09:07 UTC, cancelled at 09:17 UTC; final 64-job inventory is 21 SUCCESS / 43 CANCELLED / 0 FAILURES; **do not infer a full-domain negative** |

The three-nibble method uses **three deletion and three insertion positions**, independently chosen from nibble-index zones `[6,9], [14,17], [22,25]`; `4^6=4096` position patterns times `16^3=4096` independent replacement triplets. The two executed local runs printed respectively `mode=copied-coupon ... checks=16777216 original=0 planted=1` and `mode=route-mask ... checks=16777216 original=0 planted=1`. This differs from the previous two-unit bit/nibble/byte arbitrary indel and from odd-nibble **edge** shifts. All source checks passed.

The byte SFT has a synthetic complete preimage and checks it once per shard. Each successful GitHub shard asserts source checks, its precise `64 × 2^24 = 1,073,741,824` complete SHA256 count, synthetic positive exactly one, original target hit zero. Representative successful shard 12 printed `THREE_SEAM_COMPLETE ... checks=1073741824 expected=1073741824 planted=1 authentic=0`. Every job would exit nonzero on any original hit or failed control, so 64/64 successful jobs establish the byte copied-coupon negative above.

## Reproducers, interpretation and remaining decision

- [Byte constructor](../agents/agent40/k04_three_seam_dislocations_sft.cpp). The independent route-mask stage is selected by compiling with `ROUTE_MASK_DISLOCATION`. Sharded original-target workflows are [copied coupon](../.github/workflows/agent40-k04-three-seam-manual.yml) and [route mask](../.github/workflows/agent40-k04-three-seam-mask-manual.yml).
- [Nibble constructor](../agents/agent40/k04_three_nibble_seams_sft.cpp). Compile with or without `ROUTE_MASK_DISLOCATION` to select the two operand populations; the complete local original runs are described above.

**The retained spool is reconstructed from fragments; a dispatch ACK is not an independent bitwise certificate of its payload.** A route-field transcription could also be wrong, but no source identifies any specific mask transcription error. Both are *conditional* complete-component constructors, not a recovered historical witness. An authenticated original K04 still requires a matching full 16-byte value and its correct source/selection stage. K08's author-final words remain unquoted; the original six accepted slots remain PASS and the combined REC8/1 key remains INCOMPLETE.

**Final run reconciliation, 16 November UTC:** GitHub Actions job inventory for route-mask run `43836866630`, all 64 jobs over three pages: 21 SUCCESS, 43 CANCELLED, 0 FAILURE. Successful jobs report no original target hit; cancelled jobs provide no exclusion. The previous in-flight status and handoff request are closed. Do not resume or reinterpret the 43 cancelled shards as tested. A new producer, author-final text witness or genuinely source-conditioned stage relation has higher value.
