# K04: complete coupon from 128 row-dependent LOW IF EVEN source bits (23 Nov 2026)

**Agent33. Original K04 commitment: NO_MATCH. No recovered coupon or seventh PASS.** An exploratory complete-object test, not an authenticated reconstruction of the paper printer.

## Why this is a distinct possible output channel

The 128 intact ACK1 jobs `PS-261003-0300..0427`, exactly five minutes apart, each contain sixteen opaque payload bytes. The independently studied crew-note chain spells `LOW IF EVEN` after a specified note-row lowering. This study tests whether *one bit from a different payload byte in each row* can produce the complete 128-bit selected coupon, taking a lower bit at even-indexed jobs and a higher bit at odd-indexed jobs.

Unlike [Agent9's 128-row separable-parity 33.4m test](h17-k04-128row-separable-parity-20261105.md), the tested source selector can choose **different byte columns on successive rows**. Unlike [Agent30's print bitplane transport](h17-printer-bitplane-crossslot-candidates-20261105.md), the bit position alternates between even and odd rows while the column can vary in source-defined row-dependent patterns. This is an explicit speculative transport: the original route does not say the crew `LOW IF EVEN` instruction operated on printer jobs.

## Exact original source and target

Original printer SHA256: `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. Original routing SHA256: `f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5`. Original K04 route mask: `8556C8CB6140A7F9A5123AC7571BEE1C`. Original K04 SHA256 acceptance: `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`. The 18:02 PS-0417 ACK2 copied payload is **excluded before construction**. The 128 earlier source packets and their categorical labels are the only sampled records.

Frozen selector family: 832 `(rule,step,offset)` byte-column sequences over sixteen packet columns, comprising cyclic row index, eight-row block index, sixteen-row interleave group index, fixed column, job number's last decimal digit, CLASS category index, or DEST category index. Source row parity chooses bit pair from `(evenbit,oddbit)` in `[(0,7),(0,6),(0,5),(0,4),(0,3),(0,2),(0,1),(0,0),(7,0),(7,7)]`. Eight original/reversed row, within-byte bit and complete-byte presentation choices produce **66,560** whole-coupon presentations. Deduplicate identical complete sixteen-byte reduced components, then check full original SHA256. This yields **31,360 distinct complete original K04 commitment tests**, **zero matches**.

The separate synthetic control chooses `byte_index=(row+7) %16`, even bit 0, odd bit 7 and natural packing; sets a distinct planted SHA256 of the resulting masked component; the unchanged enumerator finds that **exact synthetic full coupon once**, showing the specified construction would be recovered if it matched. The plant does not alter original target data.

## Artifact, judgment and limits

Portable, source-hash-pinned standard-library Python reproducer: [Agent33 cross-row full K04 SFT](../agents/agent33/h17_low_even_crossrow_coupon_sft.py). Run from repo root with `python agents/agent33/h17_low_even_crossrow_coupon_sft.py resources`. The original ZIP-source local run completed at 23 Nov ~21:42 UTC, reported `position rules 832; complete_candidates 31360; original_matches 0; synthetic_positive 1`. A functionally equivalent portable file was pushed and the source-parsing regex corrected on readback. No separate remote Actions run is asserted.

This excludes **only** these 31,360 complete original components, not the actual source of an opaque physically printed coupon. The early `LOW IF EVEN` decoded note phrase is not evidence of a printer error-correction channel, and a failed K04 test does not validate that interpretation. The 128 original payloads and labels may be incidental to the keeper's personal caption. **Do not enlarge the same family without an independent source relationship or a whole intact-packet heldout predictor.**

K01, K02, K03, K05, K06, K07 still PASS; K04 and K08 MISSING, combined REC8/1 INCOMPLETE. Original `resources/`, `candidate.json` and `verify.py` unchanged.
