# K04: actual original-source-compatible full-coupon 32-bit word/interleave replay

**Agent 8 · 28 November 2026 · original SHA256 checked privately · K04 remains MISSING**

## A genuinely different complete-coupon construction

The forward xoroshiro128++ big-endian/BA PS-261003-0417 REQUESTED1 hypothesis now admits a **complete initial state**, fully enumerated in P12 parent 1371 by the earlier 16-child exact proof. Its directly serialized **24 subsequent generator outputs** supply a 192-byte candidate printer stream. The established 177-offset complete 16-byte contiguous copy family has already failed the original K04 commitment for this state.

This experiment asks a distinct, finite *copy-layout* question rather than recomputing its state: perhaps the recovered printer buffer was rearranged in four **32-bit words**, or represented four interleaved regular 32-bit lanes, before the physical 16-byte coupon was copied. The hypothesis has **no historical attestation** and is not claimed to describe the actual ESC-N printer.

Source-independent construction, applied to the 192-byte stream:

1. Extract each **contiguous 16-byte** window (177 source layouts), partitioned into four 4-byte words.
2. Separately take four 4-byte words at regular word-index strides **2..8** inside the 48-word stream (231 source layouts). Do not read beyond the 192-byte stream.
3. For each of the **408 layouts**, apply all **24 permutations** of the four words and independently reverse each word's four bytes in all **16 masks**.
4. XOR each resulting **complete 16-byte opaque coupon** with the original pinned K04 route mask and evaluate the **whole unchanged original SHA-256 K04 commitment**. No partial digest, prefilter, copied selected ACK2 fit, or disputed REQUESTED3 requirement.

Exactly **408 × 24 × 16 = 156,672** full-component assignments. On the actual source-compatible parent-1371 state the 156,672 candidate byte strings were all distinct (checked locally). The **177 unmodified contiguous-byte windows** form the prior coverage intersection; **156,495 newly distinct full-coupon byte constructions** extend it.

## Executed results

| Gate | Executed count | Outcome |
| --- | ---: | --- |
| Contiguous 4-word source layouts | 177 | Complete |
| Strided 4-word source layouts, strides 2..8 | 231 | Complete |
| All word-order/reversal constructions | 156,672 | Distinct 16-byte candidates |
| **Original complete K04 commitment hits** | **0** | **NO MATCH** |
| Extra distinct byte candidates beyond the previous 177-offset reducer | **156,495** | All commitment-negative |

The source-compatible state was independently obtained by complete exact P16 model blocking from original intact REQUESTED1, with 15 child cubes empty and one terminal child containing the sole state; the copied ACK2 was not used as a fitting observation. This report does **not** claim new source-inversion completeness: it reuses the previously established private state asset, then applies a new complete-object copy-stage family without SMT.

The final public script is [the source-safe candidate reducer](../agents/agent8/k04_fourword_interleaved_private.py), which uses the repository's [pinned source serializer](../agents/agent8/k04_bigba_forward177_replay.py) and original-source guard. Original 128-bit model and every historical candidate remain only in owner-private mode-0600 storage, not public GitHub, Actions, or this report. A synthetic-only suite independently plants **18 complete 16-byte commitment positives** (six new generator states, three layouts per state) and recovers exactly one expected full-component hit per fixture. Actual original scan returned no hit or escrow.

## Meaning / next attack

**Conditional exclusion only:** This is not evidence that xoroshiro128++ actually generated the PS-0417 printer stream, nor that a physical coupon came from the tested copy geometries. It excludes all declared four-word permutation/reversal and regular 32-bit interleave variants for **one source-compatible complete state**. It does not cover Agent7's distinct source-compatible state elsewhere in the P12 tree, source-incompatible unvisited/UNKNOWN states, other serializers, nonregular copy geometries, source resets, or a genuine original preserved coupon.

The 70-minute lease can continue on **a meaningfully different source/copy mechanism or the K08 complete-wording emitter**; repeating the same parent1371 state with another trivial word-order combination is now mathematically redundant. K01/K02/K03/K05/K06/K07 remain PASS, K04 and K08 MISSING, combined REC8/1 INCOMPLETE. No original evidence, commitment, verifier, canonical candidate or forbidden BX25 PDF was altered or opened.
