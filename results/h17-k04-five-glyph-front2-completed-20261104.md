# K04: exact-five-hex-character front-prefix fault family, complete original negative

**Agent 43 | 4 November 2026 | Finished 32/32 source-pinned jobs.** The original K04 SHA256 commitment rejected all **16,095,712,500** complete candidates in a narrowly defined five-character substitution family. This extends previous original-data exclusions for at most four copied hexadecimal characters. It authenticates no selected physical coupon bit.

## Distinct hypothesis and historical limit

The selected 3 October 2026, 18:02 UTC ESC-N/PS-261003-0417 attempt-2 RECOVER/ACK copied payload is `A9A9DC5731A5E2AE879C47215C2559D5`. The leading `A9A9` duplicated byte is unusual in this original spool but has **no independent corruption certificate**. As one possible copying error, suppose exactly five of the copied hexadecimal *characters* were substituted, with at least two among the leading four characters (`A9A9`). Hold all other characters and the route XOR mask fixed. The preserved physical/copy-stage ambiguity makes this a speculative original-commitment attack rather than a validated media model.

The unchanged route XOR mask is `8556C8CB6140A7F9A5123AC7571BEE1C`; the full K04 component SHA256 commitment is `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`. For each proposed 16-byte coupon, compute `K04 = coupon XOR mask` and `SHA256(K04)`, comparing all 32 digest bytes.

## Exactly complete search space

Choose five distinct indices from the 32 original hexadecimal characters. Require at least two of these five indices to be in 0..3. Counts by altered prefix characters:

| Changed prefix characters | Five-position sets |
| ---: | ---: |
| 2 | `C(4,2) × C(28,3) = 19,656` |
| 3 | `C(4,3) × C(28,2) = 1,512` |
| 4 | `C(4,4) × C(28,1) = 28` |
| **Total** | **21,196** |

Every selected character independently takes exactly 15 values different from the copied character. There are `15^5 = 759,375` candidates per position set, hence **16,095,712,500** complete checks; no unchanged copied glyph can masquerade as a change. Disjoint partition: enumerate ordered five-position subsets lexicographically and assign subset index modulo 32 to a runner. Original selected copied coupon is never used to fit a producer; it is only the fixed corrupted-copy baseline to alter.

## Reproducible evidence and controls

- C/OpenSSL pinned SFT: [`agents/agent43/k04_five_hex_glyph_sft.c`](../agents/agent43/k04_five_hex_glyph_sft.c).
- Manual 32-shard workflow: [`.github/workflows/agent43-k04-five-glyph-manual.yml`](../.github/workflows/agent43-k04-five-glyph-manual.yml).
- [Completed run 41759985744](https://github.com/FlareZ123/workplace-v2/actions/runs/41759985744), outcome **success**; all **32/32** matrix job conclusions **success**, 4 November 2026 at 02:25:28 UTC.
- The reproducer pins the original spool, route and acceptance SHA256 values exactly: `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`, `f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5`, `681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f`.
- Before every original search the same enumerator constructs a separate synthetic correct component with changes exactly at positions 0..4. It finds that planted full 16-byte result **exactly once among 759,375 assignments**. The synthetic `FOUND` print is deliberately distinct from the actual selected K04 commitment and does not indicate historic recovery.
- Representative original log from shard0: `RESULT mode=front2 shard=0 shards=32 eligible=21196 assigned=663 completed=663 checks=503465625 hits=0 COMPLETE`. All runner conclusions zero hits because the program exits 10 on any actual original hash match, 3 on an enumeration mismatch, 2 on a source/hash discrepancy, and 0 only on successful zero-hit complete enumeration.

## Interpretation and disjoint continuation

Under this exact same-stage same-mask **substitution-only five-hex-character model with at least two edits in the leading `A9A9` prefix**, the true original coupon is absent. The search does not exclude more than five substitutions, byte/nibble shifts, group rearrangements, different physical source, unknown mask-stage fault, or a zero-/one-prefix-character five-glyph model.

That **disjoint complementary exact-five** family has 180,180 five-position sets and **136,824,187,500** candidate assignments. It is implemented by `nonfront` mode in the same source and dispatched separately as [run 41760724947](https://github.com/FlareZ123/workplace-v2/actions/runs/41760724947) on 128 separate CI shards. **No outcome is claimed for the complementary run here.** The combined front2+nonfront partition exactly equals all `C(32,5) × 15^5 = 152,919,900,000` exact-five-character substitutions once both have completed.

K04 remains missing. The preserved exact final K08 keeper inscription also remains missing; six other individual slots PASS and original combined REC8 acceptance remains INCOMPLETE.
