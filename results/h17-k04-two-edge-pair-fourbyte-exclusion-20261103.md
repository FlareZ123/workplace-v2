# K04 selected spool: exhaustive two-end, four-byte unknown-coupon repair

**Agent 8 | 3 November 2026 23:24 UTC. Original result: NO_MATCH after exactly 4,294,967,296 original commitment checks.** No authenticated K04 coupon byte was recovered. K08 final writer-selected words remain missing; original REC8 state six individual PASS, combined INCOMPLETE.

## What changed from earlier repair enumerations

The original source-selected ESC-N printer buffer is reconstructed only from unverified spool fragments. A plausible, but entirely **unattested**, physical/copy failure could corrupt a fragment at *both ends* of an otherwise retained 16-byte buffer. This hypothesis tests exactly two independently unknown bytes at the beginning **and** two independently unknown bytes at the end. It preserves twelve interior bytes.

Source-selected route:
- 3 October 2026, 18:02 UTC, `PS-261003-0417`, `CLASS=RECOVER`, `STATE=ACK`, attempt2.
- Copied buffer `A9A9DC5731A5E2AE879C47215C2559D5`.
- Unchanged route mask `8556C8CB6140A7F9A5123AC7571BEE1C`.
- XOR-reduced, rejected original base `2CFF149C50E54557228E7DE60B3EB7C9`.
- Original unchanged K04 SHA256 target `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`.
- Original copied spool SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`.

This family covers candidate component `x0 x1 14 9C 50 E5 45 57 22 8E 7D E6 0B 3E x14 x15` for every choice of four arbitrary bytes `x0,x1,x14,x15` in 0..255. Every one of the **2^32** values is tested directly against the full, unchanged K04 digest. Since XOR with the fixed mask is bytewise bijective, this is exactly equivalent to replacing those four bytes in the underlying copied spool buffer, then applying the original mask. The payload and post-XOR stages need not be counted twice.

Prior exhaustive sources include all up-to-three-byte arbitrary replacements, all thirteen **contiguous** four-byte replacement windows, and arbitrary two-byte dislocation/reinsertion. This search targets the **disconnected** four-position quartet (0,1,14,15), whose all-four-different subset alone has **255^4 = 4,228,250,625** distinct candidates outside both the fixed-position ≤3 replacement and contiguous-four-byte replacement classes. There may be overlaps with other non-replacement fault families; none are claimed away.

## Exact computation and controls

Portable, original-source-pinned C++17 / OpenSSL / OpenMP single-file SFT: [`agents/agent8/k04_two_edge_pairs_sft.cpp`](../agents/agent8/k04_two_edge_pairs_sft.cpp), commit `ca46f5f`. The code reads the untouched original spool file and verifies its whole-file SHA256, exact selected RECOVER ACK2 line, route-mask literal and original commitment before any search. It computes the 16-byte SHA256 with a single padded SHA256 compression block. **1,000** changing-coupon ordinary `SHA256()` outputs are independently compared to the direct compression engine, all eight 32-bit words exactly. A planted complete altered four-byte coupon (first byte `42`, second `B7`, penultimate `CC`, final `39`) is assigned a synthetic in-memory SHA256 commitment, and the search must find it **exactly once** in the shard starting with first byte `42`.

The full 32-bit search was partitioned into 256 disjoint first-byte shards (each exactly 16,777,216 assignments). An independent Python standard-library batch coordinator completed four batches of 64 shards each, limiting total simultaneous native executables to four. Every shard returned exit status 0 and the expected exact completion count; all were reconciled by index0..255. No source file or acceptance oracle was modified.

| First-byte shards | Full original SHA256 checks | Original K04 matches | Planted-positive matches | Local batch log SHA256 |
| --- | ---: | ---: | ---: | --- |
| 0..63 | 1,073,741,824 | 0 | 0 (outside shard) | `ecf73d1eeefdc59bcbb6298daec321fe746aeb98b92c85b4c517106052a2b0b4` |
| 64..127 | 1,073,741,824 | 0 | **1** | `04724f07edaa4b62c4dbfa0deb903ff6d887fe92e8d9cad8769674ffc0be70bf` |
| 128..191 | 1,073,741,824 | 0 | 0 (outside shard) | `c09a688fa4b52db2ba40dbce8abdcbb1d34f14cecaad746bb3f3771a332e0455` |
| 192..255 | 1,073,741,824 | 0 | 0 (outside shard) | `6c5359c62dd3eac7bfde6305e2e197f2dd8c7940ebb7df5fb1b71b4ed822234a` |
| **All 256** | **4,294,967,296** | **0** | **1** | |

The four recorded JSON batch logs, all 256 per-shard `COMPLETE` markers, successful synthetic-positive assertion, and 2^32 total were reconciled independently after the scan. Local batch walltimes were 13.188, 13.294, 13.162 and 13.548 seconds; timing is environment-specific. The source file is portable and can run one first-byte shard to fit CI time constraints.

## Interpretive limit

The original K04 digest rules out *every* possible physical coupon within this particular disconnected 4-byte head/tail replacement family. The record does not establish that the physical buffer actually suffered this failure, that all twelve middle bytes survived, or whether a different original coupon existed altogether. This full negative may suggest pursuing independent physical provenance and source-generating architecture instead of expanding arbitrary four-byte positions. **No selected coupon bit was authenticated**, K08's exact margin caption is unobserved, and official six-PASS/two-MISSING status is unchanged.
