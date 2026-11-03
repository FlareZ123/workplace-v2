# K04: original selected ACK copy byte-stream displacement, 1..4 unknown edge bytes

**Agent 38 | 3 November 2026 | Exhaustive original-commitment negative.** The original REC8/1 remains six individual PASS; K04 and K08 unresolved, combined INCOMPLETE. No original coupon bytes are authenticated by this result.

## Different copier mechanism and exact original sources

The selected route is ESC-N / `PS-261003-0417`, **RECOVER ACK attempt2** at 18:02 UTC. Original spool `evidence/print/spool-reconstruction.log`, SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`, copies its 16 opaque bytes as `P=A9A9DC5731A5E2AE879C47215C2559D5`. Source `evidence/recovery-routing.json` supplies `M=8556C8CB6140A7F9A5123AC7571BEE1C`. The untouched original K04 commitment is SHA256(component)=`930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`.

A *hypothetical stream-displacement copy fault* may shift **every** retained payload byte and lose an unknown edge fragment of the physical 16-byte coupon. The source's printer-fax analogy and MAIL16 integrity warning motivate investigation but do not authenticate this fault.

For `n=1,2,3,4` lost bytes, two distinct complete true-paper candidate geometries are:

- **Lost original prefix**: `Q = unknown(n) || P[0:16-n]`.
- **Lost original suffix**: `Q = P[n:16] || unknown(n)`.

For every complete Q, derive `C=Q XOR M` and compare **SHA256(C)** to the original full 256-bit commitment. All unknown bytes are exhaustively varied. This is distinct from <=3-byte replacement at fixed positions, fixed-mask copier byte-lane reordering, and Agent21's adjacent-stage trials that use *different recorded rows* for their twelve fixed bytes. Our `n=4` case allows 32 **unconstrained** edge bits and 12 correctly ordered bytes taken from the *selected copied ACK2* after a shift.

## Executed outcomes and controls

| Unknown edge bytes | Complete assignments per direction | Both directions | Original K04 matches |
| --- | ---: | ---: | ---: |
| 1 | 256 | 512 | 0 |
| 2 | 65,536 | 131,072 | 0 |
| 3 | 16,777,216 | 33,554,432 | 0 |
| 4 | 4,294,967,296 | 8,589,934,592 | 0 |
| **Total** | | **8,623,620,608** | **0** |

A distinct planted full SHA256 positive for *each* direction and shift is found **exactly once** in the corresponding exhaustive range; every 2^32 case is split into eight disjoint [0,2^32) shards, each with a planted-positive expected-count check. The original source/selector, mask and exact commitment are asserted in the CI preflight; all 16 matrix jobs completed success.

- Portable C11/OpenSSL/OpenMP [single-file source](../agents/agent38/k04_ack_copier_byte_slip_sft.c).
- [Manual-only sharded workflow](../.github/workflows/agent38-k04-byte-slip-manual.yml).
- [Actual completed GitHub Actions run 41736423864](https://github.com/FlareZ123/workplace-v2/actions/runs/41736423864): **16/16 jobs SUCCESS**, 3 November 23:06–23:08 UTC. Representative original logs for shard0 show `original=0 synthetic=1` at shifts1–3 and `original=0 synthetic=0` at the first shift4 shard, with the synthetic marker located in a different shard. Last-shard logs show `original=0`. Every job's return code is zero only when synthetic count matches expectation and there is no original match.

## Meaning

The exact original K04 component **cannot** be obtained by either simple byte-stream-slip geometry with at most four unknown bytes at one edge, even when each unknown byte has every possible value. This is a model exclusion only. It does not preclude shifts with more than four unknown bytes, mixed bit/byte realignment, a different mask, selective dropout with interior faults, separate REQUESTED/ACK producers, or genuinely missing physical media. Critically the retained `P` was never authenticated independently at the physical paper stage. No certified target bit follows from a complete negative. K08 remains completely unquoted, so six original components PASS and combined REC8/1 INCOMPLETE.
