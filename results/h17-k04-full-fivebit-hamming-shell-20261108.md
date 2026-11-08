# K04 selected ACK: exhaustive complete five-bit corruption shell

**Agent 31 | 8 November 2026 | source-pinned exhaustive original commitment test.**

> **Critic prior-art correction, 8 November 2026:** This experiment is a valid independent *replication*, not new target coverage. [Workplace-v1's 17 October exhaustive K04 bit-flip bound](https://github.com/FlareZ123/workplace-v1/blob/main/results/h17-k04-bitflip-bound.md) already tested **every** Hamming weight from 0 through 6 relative to this **exact same** K04 baseline `2CFF149C50E54557228E7DE60B3EB7C9` and original commitment `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`. Its independent Python and OpenSSL runs cover all **264,566,400** weight-5 positions, including multiple bits in the same byte, and its four exact-six-bit shards cover all **5,423,611,200** positions; all original hits were zero. Thus the claimed 121,435,776 previously untested five-bit cases were **previously covered in v1**. Preserve Agent31's executed controls and log as replication evidence, but no extension to weight 6 under the unchanged baseline/mask is necessary. See [v1's genuine exact-six source](https://github.com/FlareZ123/workplace-v1/blob/main/results/h17-k04-hamming6-sharded.c).

## Objective

Recover the selected ESC-N physical coupon from the surviving attempt-2 print-spool copy under the concrete hypothesis of exactly five individually flipped bits, anywhere in its 16-byte payload. This includes five flipped bits in five different bytes and every case of two or more flipped bits in one byte. The latter cases were omitted from the earlier [five-distinct-byte search](../agents/agent2/k04_five_distinct_byte_bitflip_sft.cpp). The original six individually accepted components, immutable verifier and source remain unchanged.

## Original target

- Original spool reconstruction SHA-256: `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`.
- Exact selected timestamp/route: `2026-10-03T18:02:00Z JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER`.
- Copied payload: `A9A9DC5731A5E2AE879C47215C2559D5`.
- Recorded route mask: `8556C8CB6140A7F9A5123AC7571BEE1C`.
- Copied-mask component baseline: `2CFF149C50E54557228E7DE60B3EB7C9`.
- Unchanged original K04 component SHA-256 commitment: `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`.

For all increasing distinct bit positions `0 <= a < b < c < d < e < 128`, XOR exactly those five bits in the baseline and hash the entire resulting 16-byte component. This is a complete enumeration of exactly five bit flips and does not presume byte isolation. The XOR route mask commutes with bit flipping, so each candidate corresponds one-to-one to a hypothesized five-bit-corrected physical coupon.

## Real original-source execution

Five disjoint shards ran with the original spool SHA-pinned. Each shard separately verified its exact binomial-count expectation and a planted independent five-bit target. Shards partition on the lowest changed bit `a`.

| Lowest bit positions | Original complete SHA-256 checks | Original target hits | Planted hits |
| --- | ---: | ---: | ---: |
| [0,8) | 73,988,376 | 0 | 1 |
| [8,16) | 56,424,312 | 0 | 0 |
| [16,32) | 73,029,648 | 0 | 0 |
| [32,64) | 53,499,552 | 0 | 0 |
| [64,124) | 7,624,512 | 0 | 0 |
| **All five-bit corrections** | **264,566,400** | **0** | **1** |

The synthetic positive flips bits `0,11,33,66,127` and the enumeration finds this planted SHA exactly once. Every shard asserts its complete candidate count before accepting the run result. The original target was tested as an unmodified 256-bit digest.

### Coverage accounting (superseded by the Critic prior-art correction above)

There are `C(128,5)=264,566,400` five-bit possibilities. The previous five-distinct-byte / one-bit-per-byte experiment covers `C(16,5)*8^5=143,130,624` of these. The **121,435,776 same-byte-concentrated five-bit corrections** were omitted by the cited v2 Agent2 five-distinct-byte test, **but already exhausted by workplace-v1's 17 October full-radius experiment**. This v2 run independently reproduces the same no-hit result. Prior up-to-four-bit exhaustive checks and the present exact-five search together rule out any modification of **at most five individual bits** to this particular copied ACK / route-mask baseline.

## Outcome and limits

**No K04 original commitment match.** The actual physical selected coupon remains unknown. This rules out only a copied-payload corruption of Hamming weight <=5 *relative to the recorded XOR mask*; it does not prove the current mask is historically correct, rule out six-or-more-bit errors, a different physical capture stage or an unrelated producer. K08's exact author-final phrase remains unknown. Overall REC8/1 remains six PASS, K04/K08 unresolved, combined INCOMPLETE.

Portable C++17/OpenSSL/OpenMP test: [five-bit shell SFT](../agents/agent31/k04_fivebit_all_sft.cpp), compiled against the original spool. The source target and verifier are never modified.
