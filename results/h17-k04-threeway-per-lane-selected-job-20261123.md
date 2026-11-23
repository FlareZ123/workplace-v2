# H-17 K04: all independent 3-input Boolean merges at each word lane of the four same-job records

**Agent 24 | 23 November 2026 | Original K04 commitment NO_MATCH.** This is a complete, source-linked 16-byte coupon construction test, not a recovered physical ESC-N coupon. K01/K02/K03/K05/K06/K07 remain PASS; K04 and K08 MISSING, combined REC8/1 INCOMPLETE.

## Changed causal/copy assumption

The original spool records four distinct preserved 16-byte payloads bearing **PS-261003-0417**. In time order:

1. 16:45 UTC, LABEL/ACK, attempt 1;
2. 18:01 UTC, RECOVER/REQUESTED, attempt 1;
3. 18:02 UTC, RECOVER/ACK, attempt 2 — the selected but untrusted copied payload;
4. 18:03 UTC, RECOVER/REQUESTED, attempt 3 — later and never ACKed.

The four payloads are `E1E60D5F6B6DD2225FA6D5A2A63AD932`, `CD3E4F216ADB2FB180DA2AA90B33F7A4`, `A9A9DC5731A5E2AE879C47215C2559D5`, and `44D53DFC29D7943A95D89371DA58EC64`. All are copied sources, not authenticated physical coupon bytes. The original ACK2 payload XOR `8556C8CB6140A7F9A5123AC7571BEE1C` fails original K04 SHA256 `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`.

Explore a *word-lane-specific Boolean copy/merge* reconstruction: choose any three of the four same-job 16-byte source values and let each of the four aligned 32-bit output lanes independently be one of **all 256 Boolean functions of its three aligned 32-bit source lanes**. A source bit triplet `abc` selects one of the function's eight truth-table bits. The four output words form the complete 16-byte proposed physical coupon; XOR the unchanged route mask and check the untouched **full 256-bit original SHA256**. There is no partial-hash screening or target-based function fitting.

This is materially different from Agent27's **one shared 3-input truth table across all four words** (only 256 functions, with layouts) and Agent35's **independent 2-input truth table per word** (16^4). A word-lane copy controller could in principle perform different combination logic on different 32-bit lanes; the hypothesis remains **speculative and not source-attested**.

## Completed original results

The program enumerates every 8-bit truth table for each lane, deduplicates identical 32-bit outputs *within that lane*, and then hashes the full Cartesian product. The possible deduplications are required for an exact count, not an approximation.

| Three input records | Includes copied ACK2? | Distinct lane outputs | Full 16-byte checks | Original K04 hits | Planted full-hash hit |
| --- | --- | --- | ---: | ---: | ---: |
| LABEL, REQUEST1, ACK2 | Yes | 256,256,128,256 | **2,147,483,648** | **0** | **1** |
| LABEL, REQUEST1, REQUEST3 | **No** | 256,256,256,256 | **4,294,967,296** | **0** | **1** |
| LABEL, ACK2, REQUEST3 | Yes | 256,256,128,256 | **2,147,483,648** | **0** | **1** |
| REQUEST1, ACK2, REQUEST3 | Yes | 256,256,128,256 | **2,147,483,648** | **0** | **1** |
| **Total source-complete comparisons** | | | **10,737,418,240** | **0** | **4** |

The ACK2-withheld cohort is the direct physical-coupon reconstruction branch: no selected copied byte enters that candidate's input, but the **later 18:03 requested** record does, so this is a *retrospective copy reconstruction*, not a causally prior emission algorithm.

Each model independently synthesizes one planted full component by choosing 8-bit functions `96,E1,A8,37` for its four lanes, XORing the original route mask and hashing. Its **same exhaustive 16-byte search** recovers the planted component exactly once. All four controls pass. This verifies source-boundary parsing, full-byte serialization, route XOR and complete SHA256 comparison on a recoverable synthetic candidate. It does not validate that a real printer or OCR copy channel used these gates.

Original-source checksums are asserted before iteration: spool `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`, route `f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5`, acceptance `681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f`. Genuine source, routing, acceptance and canonical candidate were read-only.

## Reproduction and scope

SFT: [`agents/agent24/k04_threeway_lane_boolean_sft.cpp`](../agents/agent24/k04_threeway_lane_boolean_sft.cpp). From the repo root:

```sh
g++ -O3 -march=native -std=c++17 -fopenmp -Wno-deprecated-declarations \
  agents/agent24/k04_threeway_lane_boolean_sft.cpp -lcrypto -o /tmp/k04-threeway
OMP_NUM_THREADS=5 /tmp/k04-threeway resources 1
OMP_NUM_THREADS=5 /tmp/k04-threeway resources 0
OMP_NUM_THREADS=5 /tmp/k04-threeway resources 2
OMP_NUM_THREADS=5 /tmp/k04-threeway resources 3
```

Local original-source completion times for the four cohorts were 87.427, 46.155, 46.061 and 43.366 seconds respectively on five visible cores. Full machine logs were independently captured and compared to the declared cardinalities; each cohort's worker returned exit code zero with `planted_hits=1`.

**Interpretation:** the complete fixed-alignment, three-source, arbitrary-per-word-bitwise-Boolean family yields no original accepted component. This does not exclude a four-input function, physical paper/print transform, byte/word relayout, nonbitwise ECC, a separate producer, or the absent physical coupon. It does not establish any source-selected original coupon bit and supplies no K08 final wording. Do not extrapolate the negative to all same-job copy mechanisms or claim combined recovery.