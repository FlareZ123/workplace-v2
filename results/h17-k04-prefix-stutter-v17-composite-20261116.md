# K04: leading-byte stutter plus V.17/V.29 receive-stream descrambling

**Agent 7 | 16 November 2026 | 4,294,967,296 complete original K04 commitment checks, zero matches.** This is an exploratory composition of two observations from the surviving record, with one exact planted positive. K04 and K08 remain unresolved.

## Distinct, frozen source-to-complete-coupon model

The retained selected `PS-261003-0417` `RECOVER` attempt-2 ACK at 18:02 UTC has copied bytes `A9A9DC5731A5E2AE879C47215C2559D5`. The consecutive `A9` prefix suggests a *possible* one-byte copy stutter. N22's informal complaint that the label printer thinks it is a fax machine suggests a *possible* fax bitstream operation. Neither observation establishes an actual stutter, firmware, or physical coupon. Earlier work checked these phenomena separately; the present model first corrects a **specific byte-loss hypothesis**, then applies the exact V.17/V.29 23-bit self-synchronizing receive descrambler.

1. Treat the **second** `A9` as a duplicated copy, delete it, slide the surviving 14 trailing bytes left, and append one **unknown trailing raw byte** `x` in `0..255`. The complete 16-byte hypothesized physical input is `A9DC5731A5E2AE879C47215C2559D5xx`.
2. Interpret that 16-byte input as a receive bitstream in either MSB-first or LSB-first order. Enumerate every possible 23-bit preceding received-bit history `h` in `[0,2^23)`. Descramble using the standard recurrence `d[n] = s[n] XOR s[n-18] XOR s[n-23]`.
3. Apply the **unchanged** original route mask `8556C8CB6140A7F9A5123AC7571BEE1C` via bytewise XOR to the entire 16-byte descrambled buffer. Compare **all 256 bits** of `SHA256(component)` to the unchanged original K04 commitment `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`.

This is a conditional alternative physical-copy-plus-receiver model. It does not use the disputed ACK2 as an independently authenticated coupon, and it does not claim N22 identifies a historical ESC-N modem.

## Complete result

| Bit order | Prior states | Unknown final input bytes | Complete original checks | Hits |
| --- | ---: | ---: | ---: | ---: |
| MSB first | 8,388,608 | 256 | 2,147,483,648 | 0 |
| LSB first | 8,388,608 | 256 | 2,147,483,648 | 0 |
| **Both** | | | **4,294,967,296** | **0** |

The run used 16 disjoint manual batches `shard:0:16`, `shard:16:16`, ..., `shard:240:16`. Each covers 16 disjoint high-state indices, and exactly `268,435,456` complete original checks over both bit orders. All 16 batches completed with zero original hits. The independent synthetic complete-coupon target, generated from a known history `0x5A3C12`, MSB order and missing input `0x42`, was recovered **exactly once** in batch `shard:176:16`. Each batch passed 512 OpenSSL `SHA256(data,16)` versus one-block `SHA256_Transform` differential controls. Additional direct-recurrence/basis controls passed for representative histories. 

Because the descrambler's history affects only the first 23 output bits and the trailing unknown input byte maps bijectively to the final output byte, the implementation enumerates every possible **final output byte** instead of recomputing all 256 input variants. This preserves the exact output candidate set and complete assignment count. The 23 history-bit effects are computed as linear basis differences and exhaustively enumerated with 15-bit Gray code inside each shard.

Original spool SHA256 verified: `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. The selected ACK line, original route mask, and original K04 full commitment were checked before work. Original records, canonical candidate, verifier and commitments were untouched.

## Reproduction and scope

Source-pinned, standalone C++17 + OpenSSL + OpenMP reproducer: `agents/agent7/k04_prefix_stutter_v17_sft.cpp`. Build with a C++17 compiler and `-O3 -fopenmp -lcrypto`. Pass the original `resources` directory and `shard:<start>:<count>`; each 16-high-state batch is independent. `pilot` runs the first high-state partition, and `all` runs every partition in one process.

**Conclusion:** no accepted K04 component exists in this exact stutter-plus-V.17/V.29-receive-descrambler family. This does not exclude other error locations, longer copy disruptions, alternate printer framing, different protocols, a selected coupon from a distinct source, or the missing physical original. It provides zero authenticated selected K04 component bits and no information about K08's author-final phrase. The original six already accepted slots remain unchanged and combined REC8/1 remains INCOMPLETE.
