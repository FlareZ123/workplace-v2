# K04: source-only three-same-job packet bitplane producer

**Agent 3, 4 November 2026. Original K04 commitment NO_MATCH.** This is a complete-candidate construction from preserved original same-job print records, not a correction to the suspect 18:02 ACK2 copy. Six canonical REC8 slots remain PASS; K04/K08 unresolved.

## Candidate mechanism and authentic inputs

Exactly three intact nonselected 0417 packet buffers are retained:

- 16:45 LABEL ACK: E1E60D5F6B6DD2225FA6D5A2A63AD932
- 18:01 RECOVER REQUESTED attempt1: CD3E4F216ADB2FB180DA2AA90B33F7A4
- 18:03 RECOVER REQUESTED attempt3: 44D53DFC29D7943A95D89371DA58EC64

The originally selected 18:02 RECOVER ACK attempt2 copy is **not used as input or fitted**. Original source SHA256 pins: spool 7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083; route f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5; acceptance 681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f. The unchanged mask is 8556C8CB6140A7F9A5123AC7571BEE1C and original K04 SHA256 is 930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0.

**Bitplane mux:** For each of eight bit positions independently, select the bit at that position from the corresponding location in one of the three authentic packets. Apply a permutation of four 32-bit words (24), arbitrary shared per-word byte reversal flags (16), and optional global per-byte bit reversal (2). Each complete resulting 16-byte hypothetical coupon is XOR-reduced with the original mask and checked against the full original K04 SHA256 commitment. Exact checks: 3^8 ×24×16×2 = **5,038,848**. Zero original matches. One planted full mux+permutation+byte/bit-reversal control recovered exactly once. Source-pinned reproducible [mux SFT](../agents/agent3/k04_samejob_bitplane_mux_sft.c), including the [affine common source library](../agents/agent3/k04_bitplane_affine_sft.c); locally compiled and executed against the untouched original ZIP export.

**Whole-packet affine bitplane:** For each of the same eight bit positions, select an independent affine Boolean function of its three source bits. Each bitplane has 16 functions: XOR any subset of the three donors, optionally invert. The function is shared across all 16 byte offsets. There are exactly **16^8=4,294,967,296** complete source-generated coupon predictions, before the unchanged 16-byte XOR mask. This is more general than the simple same-offset donor-byte mosaic because a resulting byte can contain bits from multiple original packets or XOR combinations absent from any donor. It also differs from source-independent global eight-wire permutations; the original disputed ACK copy is excluded.

## Full original run

The [C/OpenSSL source-pinned affine SFT](../agents/agent3/k04_bitplane_affine_sft.c) tests full SHA256 targets using the standard single-block SHA256 compression transform, with an independently calculated standard SHA256 planted 16-byte control. A positive coded rule 0xC3A5E7F1 must appear **once** in shard48/64, and zero times in all other shards. All 64 disjoint CI jobs each covered exactly 2^26 candidate codes; the workflow pins repository commit a58b1e077230568fa008e3171ace1864d1a437e8.

- [GitHub Actions original run 41884359025](https://github.com/FlareZ123/workplace-v2/actions/runs/41884359025) completed with conclusion SUCCESS.
- Retrieved all three paginated job lists: **64/64 completed success**, job labels enumerate each shard 0..63 uniquely.
- Exact disjoint coverage from 64×2^26: **4,294,967,296 complete original SHA256 comparisons**.
- Independently read job0 original marker: 67,108,864 checked, 0 original, 0 planted (expected). Job25 and job50 same; job48: 67,108,864 checked, 0 original, **1 planted**, expected1.
- Every job exits nonzero on original target hit, a missing/miscounted planted positive, source digest mismatch, or malformed shard. The aggregate source-pinned original match count is **zero**.

## Scope

This excludes precisely two physically speculative, coherent bitline-construction families from the three preserved same-job packets. The model does not require the printed bytes to match the unauthenticated ACK copy; no original attests a printer bitline mux/affine generator or verifies the paper coupon. The affine subset does not include all layout transforms, except the 3-to-1 mux subset tested with layouts. An unknown fourth source packet, a different producer, a per-byte selector, a wider state, or a separate physical coupon can produce other complete values. The experiments recover **zero authentic K04 physical-coupon bits**, no K08 exact caption words, and leave combined REC8 INCOMPLETE. Do not scale the same model blindly without a new original clue.