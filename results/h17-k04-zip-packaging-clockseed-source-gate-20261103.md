# K04: original ZIP packaging clock as alternate seeded-printer source

**Agent10 | 3 November 2026. Source-first, bounded original-data negative.** The authentic selected K04 coupon remains unrecovered; six other REC8 keys PASS, K04/K08 missing, combined INCOMPLETE.

## Why this is distinct

The prior [incident-clock global seed gate](h17-k04-global-clockseed-longphase-source-gate-20261103.md) exhausts integer UTC seconds across **2–5 October 2026** plus calendar-derived integer seeds, searching the first 8192 native CPython MT19937 output words. The present test instead uses a **different, actual preserved source timestamp**, from the ZIP's **extended UTC file metadata**. The data export's earliest UT field is **2026-10-20 04:12:14 UTC**, sixteen days after the incident. Under the hypothesis that a synthetic archive-generation/packaging process initialized a deterministic printer-coupon stream from its own wall-clock seconds, this supplies a new source-defined seed center absent from the incident-clock tests.

This is speculative. The ZIP timestamp establishes an export packaging clock only; it does **not** prove the original print hardware, print buffer or historical coupon was ever seeded by that timestamp. The test is valuable only as a finite, source-gated check of that very specific alternative provenance model.

## Original source and complete test

- Original attached ZIP SHA-256 **\`e778552c555fac652e24fd09e1c4f31bd066b4686e624b91f6e94e1d64342bf7\`**, 46 non-directory members; first ZIP UT field \`1792469534\`, interpreted in UTC. Source independent of the internal file's 4 Oct 2026 preservation date.
- Original printer \`resources/evidence/print/spool-reconstruction.log\`, SHA-256 **\`7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083\`**. The first undisputed intact ACK \`PS-261003-0300\` has exact 16-byte payload \`FBBBC54356483F5864BB3F06794518A5\`. Its bytes are a withheld *heldout target for the generator*, with no use of disputed K04 ACK2, original K04 acceptance hash or mask. All 132 other original printer rows are unused.
- Enumerate **all 172,801 integer-second seeds** from UTC **19 October 2026 04:12:14** to **21 October 2026 04:12:14 inclusive**. For each \`random.Random(seed).randbytes(8192*4)\`, inspect every 16-byte packet from four consecutive 32bit-native output words, at every aligned start **0..8188**. Admit every permutation of the four words and independent byte reversal of any word (24 × 16 = **384** complete serializers).
- Total **1,415,067,389 source packet positions**, each permitting the 384 serializers; an eight-prefix native-word filter reduces candidate fullpacket comparisons without excluding any serializer. The source gate saw **one fourbyte first-word collision** in the entire run and **zero complete firstpacket matches**.
- Synthetic control: a planted packet from true seed \`1792469534+57\` at word start183, reordered and partially reversed at fourword granularity, is fully recovered by the same code. A onebyte mutation of that packet is rejected. An optional \`--zip\` argument re-authenticates the original ZIP hash and UT timestamp; the repo's \`resources/\` otherwise suffices.

## Outcome and caveats

The entire specified **packaging-clock, whole-second CPython MT stream** family fails the original intact first-packet source check, even after all fourword orientations and 8192-word prefix phases. No K04 commitment probes were necessary and **no candidate original coupon** emerged. This is a stronger test of that source-anchored clock alternative than checking a single guessed export-second seed, and it is disjoint in clock window from the incident-date prior art.

The test does not cover subsecond seeds, independent emitter streams per job, non-CPython MT initialization, other encryption/PRNG engines, longer phase offsets, source-copy corruption of the first intact packet, or the historically selected ACK's physical media integrity. It cannot prove that K04 is unsolvable; it closes only this conditional model. The observed ZIP timestamp is **not independent proof that the source data was generated then**. Do not extrapolate this finite negative into an archive-wide original-evidence exclusion.

[Single-file standard-library source-gated SFT](../agents/agent10/k04_zip_packaging_clockseed_sft.py) with synthetic positive and immutable-source SHA controls. Run with \`--zip original.zip\` when the uploaded ZIP is accessible. The original source/verifier/acceptance files remain untouched.
