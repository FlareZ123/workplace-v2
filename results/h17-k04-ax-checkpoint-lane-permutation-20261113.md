# K04 AX checkpoint lane-permutation search (13 November 2026)

## Question

Could the missing 16-byte K04 component be a reordered representation of one of the complete AX transfer checkpoint vectors, rather than the printer-route payload? This is an exploratory alternative shared-export/reducer hypothesis; the recorded K04 route still points to the ESC-N printer job.

## Source-pinned inputs

The test reads the original source records and acceptance material without modifying them:

| File | SHA-256 |
|---|---|
| `resources/evidence/transfers/transfer-audit.jsonl` | `32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf` |
| `resources/acceptance.json` | `681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f` |
| `resources/evidence/recovery-routing.json` | `f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5` |

The eight complete vectors are the eight sequence-ordered 16-byte concatenations of the two attempts for each transfer:

| Transfer / attempt | Checkpoint vector (hex) |
|---|---|
| AX-7778 / 1 | `83360E7B368DAEDE7CA7537AFE7835FD` |
| AX-7778 / 2 | `AC5FBCDD1CB5C98CA234AE35DD42B16A` |
| AX-7781 / 1 | `1E358C9396C494EA2651BB39D0ECBE7B` |
| AX-7781 / 2 | `CD8A9A4A42B5E7893086CC5B3E762AEF` |
| AX-7782 / 1 | `62244DFBF3B8CA3D1888F22A3DB08769` |
| AX-7782 / 2 | `8947CEDCB9CC73BAB7E87BE63302C5C9` |
| AX-7783 / 1 | `8311FBED0A980B7497367C8DD72E2E3A` |
| AX-7783 / 2 | `434779531E2D995B670DD08D4125CBA2` |

## Candidate construction and result

For each vector, enumerate every permutation of its eight 16-bit checkpoint lanes (`8! = 40,320`) and every independent per-lane byte-order choice (`2^8 = 256`). For each resulting 16-byte candidate, test both:

1. the candidate directly as K04; and
2. the candidate XOR the original 16-byte K04 `masked_component` from the routing file.

This is **10,321,920 layouts per vector**, **82,575,360 candidate layouts overall**, and **165,150,720 full SHA-256 commitment checks** against the original K04 slot commitment `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`.

**Result: zero K04 commitment hits.**

The implementation also passed a planted positive control. For vector AX-7778/attempt 1, permutation `[7,0,5,2,1,4,3,6]` and byte-swap mask `0xA5` produce `FD3583367A53368D0E7BA77CAEDE78FE`, whose SHA-256 is `bde741c1581e3a0bb51b80ddc38650f13aafc93b51fb07ce86bc6d239a89fc52`. Running the same enumerator with that digest as the target recovered exactly that planted candidate.

## Reproduction

The source-pinned C++ implementation is [`agents/agent50/k04_ax_checkpoint_lane_permutation_sft.cpp`](../agents/agent50/k04_ax_checkpoint_lane_permutation_sft.cpp). It verifies the three source-file hashes, extracts all eight complete vectors from the transfer audit, reads the original K04 target and mask, and supports bounded `--start` / `--end` vector ranges plus a synthetic `--target` for the positive control.

Example (from the repository root):

```sh
g++ -O3 -march=native -std=c++17 agents/agent50/k04_ax_checkpoint_lane_permutation_sft.cpp -lcrypto -o /tmp/k04-ax-permute
/tmp/k04-ax-permute
```

Positive control:

```sh
/tmp/k04-ax-permute --start 0 --end 1 --target bde741c1581e3a0bb51b80ddc38650f13aafc93b51fb07ce86bc6d239a89fc52
```

## Interpretation and boundary

This closes only the exact family “one complete transfer-attempt checkpoint vector, reordered as eight 16-bit lanes with independent byte swaps, then direct or prescribed K04 mask-XOR reduction.” It does **not** test arbitrary bit transformations, per-sequence cross-transfer mosaics, chunk contents, or unrelated reducers. It does not authenticate a relationship between the transfer audit and the physical ESC-N coupon, and it yields no K04 bits.

Do not widen this into arbitrary checkpoint transformations without an independent source-defined reason. The six already accepted slots remain unchanged; K04 and K08 remain missing.
