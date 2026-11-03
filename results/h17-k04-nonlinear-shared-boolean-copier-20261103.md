# K04: nonlinear same-job bitwise coupon producer, exhaustive global truth tables

**Agent 8 | 3 November 2026.** The untouched original K04 commitment accepted **zero** complete candidates in a new finite, source-selected nonlinear class. The official six accepted slots remain PASS; K04 and K08 remain unresolved, combined INCOMPLETE.

## Why this is a different target-reaching mechanism

The selected ESC-N printer event is the 18:02 UTC `PS-261003-0417`, `CLASS=RECOVER`, attempt-2 ACK. The copied ACK proves dispatch, not physical-media fidelity. Four records survive for that exact job: a 16:45 LABEL ACK, 18:01 RECOVER REQUESTED, the 18:02 RECOVER ACK copy, and 18:03 RECOVER REQUESTED. If a shared bitwise copier or retry-combiner built the physical coupon, its output bits might be a **nonlinear Boolean function** of bits at the same position in these preserved source buffers.

Earlier [four-source byte mosaics](h17-k04-four-source-same-job-copy-mosaic.md) exhaust independent donor-**byte selection**, and the [per-word XOR](h17-k04-retry-xor-word-producer-sieve.md) and [additive retry](h17-k04-retry-additive-word-producer-sieve.md) models exhaust named arithmetic forms. This experiment permits each output byte to consist of individual bits computed by an arbitrary **shared nonlinear truth table**, including AND, OR, majority, asymmetric gates, complements and arbitrary mixed nonlinear functions. No historical hardware document establishes such a gate; it is an exploratory full-coupon hypothesis.

## Exact source-constrained enumeration

Input file `resources/evidence/print/spool-reconstruction.log`, original SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. The four job payloads, in chronology:

1. LABEL ACK: `E1E60D5F6B6DD2225FA6D5A2A63AD932`
2. RECOVER REQUESTED1: `CD3E4F216ADB2FB180DA2AA90B33F7A4`
3. RECOVER ACK2 copied: `A9A9DC5731A5E2AE879C47215C2559D5`
4. RECOVER REQUESTED3: `44D53DFC29D7943A95D89371DA58EC64`

For each output bit position, read the corresponding bit from each of the selected input buffers and treat that vector as an index `p` in a single shared truth table `T`. Set output bit to `(T >> p) & 1`. The truth table is applied identically to all 128 bit positions, with the original bit and byte alignment preserved. Two independent stages are checked: the constructed coupon XOR the unchanged original mask `8556C8CB6140A7F9A5123AC7571BEE1C` (historical route reduction), and the constructed coupon directly (hypothetical stage reinterpretation). In both cases, compare SHA256 of the complete 16-byte candidate to the original K04 SHA256 commitment `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`.

Two finite models:

| Input role | Complete truth tables | All input profiles occur? | Coupons already in four-source same-byte mosaic | Coupons outside that mosaic | Real K04 hits, both stages |
| --- | ---: | --- | ---: | ---: | ---: |
| Three nonselected buffers (LABEL ACK, REQUESTED1, REQUESTED3) | 256 | Yes: 8/8 | 3 | **253** | **0** |
| All four job buffers, including copied ACK2 | 65,536 | Yes: 16/16 | 4 | **65,532** | **0** |
| **Total** | **65,792** | | | | **0** |

All input bit patterns occur, so the 256 and 65,536 generated coupons are pairwise different **within each respective model**. Counts of coupons outside the predecessor mosaic are exact at the byte-value level; there may be overlap between the two current families and other predecessor fault models. Each model makes two complete SHA256 stage checks, giving 131,584 actual original-target comparisons.

## Original execution and controls

The portable, read-only [single-file Python SFT](../agents/agent8/k04_boolean_copier_sft.py) selects the exact retained job rows and asserts the spool source digest. It independently plants a deliberately nonlinear truth table in each input model (`0x96` and `0x6996` respectively), commits its correctly masked full 16-byte output to an in-memory test digest, and rediscovers the planted candidate **once in each model**. The source-original search returns:

```text
three_earlier_or_later: 256 distinct coupons, 253 outside prior byte mosaic, 0 authentic hits, 1 planted hit
four_including_ack_copy: 65536 distinct coupons, 65532 outside prior byte mosaic, 0 authentic hits, 1 planted hit
```

Executed locally against the unmodified uploaded 46-member H-17 archive; portable script's local Git blob SHA1 `a4bd9d8fb2e76126d3175fa849c97606c3f86170` matched the published remote blob after commit `72ba78d`. Source, original verifier, acceptance inventory and canonical six-slot candidate were never changed.

## Boundary and next question

A **single fixed bitwise Boolean gate of up to four same-job preserved buffers** cannot produce the accepted K04 candidate in either tested source stage. This eliminates a class of whole-buffer nonlinear repair/producer functions that are absent from exact byte mosaics and word-level linear arithmetic. It does not exclude per-word or time-varying truth tables, bit-phase shifts, independently generated missing bytes, or the original unobserved paper coupon. There is no original evidence selecting the gate model, so the negative should not motivate arbitrary larger Boolean expression enumeration without a new genuine source-stage discriminator. A successful direction would connect a complete source-object prediction to a second, role-matched intact ACK2, or identify a source record indexing the selected stage. No authentic selected K04 bit follows from this negative; K08's writer-final phrase remains open.
