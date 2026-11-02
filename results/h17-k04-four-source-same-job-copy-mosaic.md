# K04: exhaustive four-source same-job printer buffer mosaic

**Agent 16 | 2 November 2026. Status: original K04 commitment NOT matched, no recovered coupon.** Read-only historical-source candidate-generation experiment.

## Target-facing mechanism and difference from previous work

The selected physical north coupon `ESC-N / PS-261003-0417 / RECOVER / ACK attempt 2 / 18:02 UTC` is represented only by a reconstructed, unauthenticated 16-byte print buffer. Under a speculative **cross-class stale-buffer contamination** mechanism, the received coupon could be constructed byte by byte at identical offsets from any of the job's four surviving 16-byte buffers:

| Donor | Class / ACK status | Preserved hex bytes |
| --- | --- | --- |
| 0417 attempt 1, 16:45 UTC | LABEL, ACK | `E1E60D5F6B6DD2225FA6D5A2A63AD932` |
| 0417 attempt 1, 18:01 UTC | RECOVER, REQUESTED | `CD3E4F216ADB2FB180DA2AA90B33F7A4` |
| 0417 attempt 2, 18:02 UTC | RECOVER, ACK, copied | `A9A9DC5731A5E2AE879C47215C2559D5` |
| 0417 attempt 3, 18:03 UTC | RECOVER, REQUESTED | `44D53DFC29D7943A95D89371DA58EC64` |

The fourth, earlier **LABEL ACK** is a distinct same-job source. This search strictly extends the **three-RECOVER-buffer 3^16 = 43,046,721** test already exhausted in v1 [`results/k04-byte-mosaic.c`](https://github.com/FlareZ123/workplace-v1/blob/main/results/k04-byte-mosaic.c). A prior three-source failure does not exclude involvement of this fourth preserved buffer. This experiment makes the new transfer hypothesis explicit; it does not establish that the physical copying mechanism truly shared bytes across classes.

## Exact evaluation and controls

Let `D0..D3` be the above four original buffers, and let `M` be the unchanged route XOR mask `8556C8CB6140A7F9A5123AC7571BEE1C`. For each independent selector vector `s[0..15]` in `{0,1,2,3}^16`, form `candidate[i] = D[s[i]][i] XOR M[i]` and compare its complete SHA-256 digest with the **untouched** K04 acceptance commitment `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`. Four bytes at each of 16 positions are distinct, so all **4,294,967,296 selector assignments produce different full component values**.

Read-only reproducible C++/OpenSSL/OpenMP single-file test: [`agents/agent16/k04_four_source_mosaic_sft.cpp`](../agents/agent16/k04_four_source_mosaic_sft.cpp). Source spool SHA-256 pinned as `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`; four source hex bytes are frozen from that original. Enumeration uses base-four reflected Gray-code state updates across 14 byte positions, while each shard fixes the two remaining positions. The code includes a synthetic ground-truth component made from three specified donor choices; its **unique** expected commitment match must appear in shard 6, separately from the original target.

Completed 2 November local GNU C++ / OpenSSL execution with four concurrent disjoint jobs, one native thread each:

| Shards | Complete candidate SHA-256 checks | Original matches | Synthetic control hits | Elapsed seconds |
| --- | ---: | ---: | ---: | ---: |
| 0–3 | 1,073,741,824 | 0 | 0 (not in range) | 453.273 |
| 4–7 | 1,073,741,824 | 0 | **1 (PASS)** | 454.676 |
| 8–11 | 1,073,741,824 | 0 | 0 (not in range) | 449.286 |
| 12–15 | 1,073,741,824 | 0 | 0 (not in range) | 455.125 |
| **Entire exact four-source family** | **4,294,967,296** | **0** | **1 (PASS)** | parallel execution |

Every job exited code 0, every scheduled shard printed its completion marker, and the original target match count was zero. No official evidence, mask, acceptance file, candidate or verifier changed. The synthetic control is only a programming check, not an authentic historical K04 coupon.

## What this excludes, and next avenue

**Excluded under the stated model:** any 16-byte K04 original coupon assembled from the four known 0417 buffers by choosing exactly one donor byte **at the same byte offset** for each output position, then XORing with the currently transcribed route mask. The full 3^16 predecessor family is a proper subset of this negative.

**Still open:** cross-offset reassembly, independent missing printer media, an incorrect mask or buffer stage, a producer-origin correction that yields bytes absent from all four preserved buffers, and K08 final text. The model has no original proof of physical inter-class mixing. Do not promote this finite negative to an authentication or selected-bit recovery; K04 original selected bits remain unproved, K08 exact final caption remains open, and combined REC8/1 acceptance is **INCOMPLETE**. A stronger next experiment should supply a source-derived, testable producer or transfer rule reaching the selected component rather than extending arbitrary donor-choice alphabets indefinitely.
