# K04: independent two-stage copied-payload and route-mask serializer transforms

**Agent12 | 3 November 2026 | Complete K04-candidate exploratory test: zero original matches.** Official recovery remains six PASS, K04/K08 missing, combined INCOMPLETE.

## Different candidate-construction mechanism

The original incident reduction is \`C = P XOR M\`, where \`P\` is the reconstructed original printer's selected ESC-N RECOVER ACK2 coupon and \`M\` is the separately transcribed route mask. The \`P\` copy has no independent media integrity, and the route sheet is a separate transcription. Earlier source-pinned work tested the same row/column, fourword and word-byte orientations against **only one operand at a time**:

- [Agent9](h17-k04-selected-copier-byte-lane-fault-sieve.md) and [Agent5](h17-k04-lanewire-permutation-sieve.md), copied-payload permutations holding mask fixed.
- [Agent30](h17-k04-mask-stage-serialization-sieve.md), mask permutations holding copied payload fixed.

The new hypothesis allows **two independent finite serializer interpretations**, one applied to each original operand **before XOR**. This produces new complete reduced candidates that earlier one-sided tests never examined. There is no original witness that both source channels were independently corrupted, so this is a speculative two-fault model and cannot validate a physical copier fault from a zero-hit outcome.

## Frozen source, finite algorithm and original commitment

Read only the original pinned printer spool (SHA256 \`7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083\`). Select exactly job \`PS-261003-0417\`, \`RECOVER\`, \`ACK\`, attempt2, \`2026-10-03T18:02:00Z\`.

- Copied \`P0 = A9A9DC5731A5E2AE879C47215C2559D5\`.
- Transcribed \`M0 = 8556C8CB6140A7F9A5123AC7571BEE1C\`.
- Original, untouched K04 SHA256 target: \`930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0\`.

For **each** of \`P0\` and \`M0\`, independently choose a 4×4 byte-matrix row-major or transposed/column-major view, permute all four resulting 4-byte words (4!), and reverse or preserve byte order independently in each output word (2^4). This yields **768 unique transformed payloads** and **768 unique transformed masks**. For their exact Cartesian product, hash every 16-byte \`C=transformed_P XOR transformed_M\` against the full unchanged K04 SHA256; also count final reduced-candidate collisions, to avoid double-counting raw transformations.

## Empirical results

| Quantity | Count |
| --- | ---: |
| Independent payload-side layouts | 768 |
| Independent mask-side layouts | 768 |
| Two-stage complete SHA256 checks | **589,824** |
| Distinct final reduced \`C\` candidates | **589,824** |
| Final \`C\` values already reachable by either side alone | **1,535** |
| **New reduced \`C\` candidates beyond both one-stage layout families** | **588,289** |
| Authentic original K04 commitment matches | **0** |
| Planted genuine dual-stage full-hash positive | **1 exact match** |

The planted positive selected two non-identity layouts, generated their true reduced component, then searched the complete same two-stage product against its independently constructed SHA256 commitment. It appeared **exactly once**. Source selection, route mask and real target hash are asserted by [the standalone standard-library SFT](../agents/agent12/k04_dual_stage_serializers_sft.py). An independent local equivalent enumeration of the original source completed in about 1.2 seconds and yielded the counts above. The committed script has not separately been run in CI.

**Coverage distinction:** This does not repeat the old hash checks under a different name: **588,289** fully specified final 16-byte values are new relative to the corresponding one-sided 768+768−1 set. Those candidates still arise from an unattested two-fault causal explanation. Other independent masks, nonpermutation byte changes, lost physical media fragments, and different upstream source objects remain open. A future two-stage fault model should be supported by a real cross-channel serializer or source-original comparator before larger expansions.

The negative does not authenticate one original physical selected coupon bit; K08 exact author-final keeper wording remains unknown. **K01/K02/K03/K05/K06/K07 are individually PASS; K04/K08 unresolved; combined REC8 INCOMPLETE.** All original resource files, verifier, acceptance and canonical candidate remain unchanged.
