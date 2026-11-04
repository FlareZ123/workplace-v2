# K04: cyclic MT624 source-state phase expansion, 61.3 million complete coupon candidates

**Agent 8 | 4 November 2026, 22:53 UTC | original K04 commitment: 0 matches.** The surviving source data remain untouched. K01/K02/K03/K05/K06/K07 individually PASS, K04/K08 unresolved, combined REC8/1 incomplete.

## New construction and actual coverage

Four unrelated original records contain an unusually exact **624 preserved 32-bit words** when the disputed selected printer record is completely withheld: 528 words from 132 other printer packets, 88 opaque CONTROL values from the complete raw recorder, four K01 signed ink groups and four approved K06 revision-C strips. This source count has already motivated the earlier [four-stream MT contiguous mosaic](h17-k04-624word-fourstream-mt-mosaic-20261104.md), [post-state fourword test](h17-k04-mt624-complete-before-after-coupon-20261104.md) and [whole-pool-as-native-state 976m output-window test](h17-k04-624word-pool-as-mt-state-20261104.md). None recovered K04.

The **increment here is a circular SOURCE-STATE boundary**, beyond the conventional fixed first word and beyond inspecting the windows of one already twisted state. Suppose the original full 624-word source state was stored with an arbitrary *circular* phase, and the printer coupon was emitted immediately after interpreting that rotated array as a complete MT19937 internal state. For every original conventional block layout, independently shift the 624 entries through **all 624 possible phase offsets** *before twisting*, predict four complete native outputs using the MT twist relation, serialize four words, XOR the original route mask and test the unchanged K04 SHA256 commitment. This creates new candidates for offsets across the MT in-place recurrence boundary.

The earlier one-twist state-window experiment does overlap a subset of these candidates when a phase lies wholly in the first 227 old-state positions: the recurrence uses only untwisted words in that region. The new test's phases crossing and beyond that boundary require recomputing the state relation in a rotated coordinate frame; these are not generally identical to later windows of the fixed-orientation, in-place twisted state. Do not count all 61.3m comparisons as independent previously untouched coupons.

## Exact source and computations

- Source SHA256 spool: `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`.
- Source SHA256 recorder: `5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba`.
- Unique withheld target source: 3 Oct 2026 18:02 UTC, `PS-261003-0417`, RECOVER ACK attempt2, copied bytes `A9A9DC5731A5E2AE879C47215C2559D5`, explicitly never used as an inferred coupon.
- Approved K01 source words in recorded A–D order: `049AAB2E 1CDE7A82 CD7C6023 4303C91A`. Approved K06 C strips in SERVICE_ORDER: `5DBF40EE 52FAAED9 A536D332 6CF0D95A`. The script compares both against their original independently accepted full SHA256 slot commitments.
- Original route mask: `8556C8CB6140A7F9A5123AC7571BEE1C`, read and checked against the route sheet; original full K04 digest `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`, read and checked against the acceptance JSON.

The same **12,288** source block layouts as Agent39's conventional test comprise 24 whole-group orderings, eight printer orientations and four independent endian/reversal configurations for each of the other three groups. Each group value is interpreted as a tempered MT output and untempered before placement. For each of **624** phases, compute four first-after-state outputs using the standard `(a & 0x80000000)|(b & 0x7fffffff)` twist splice and offset397, with circular indexing into the *pre-twist* pool. Test eight complete 16byte coupon serializers: native/tempered, per-word big/little endian, forward/reverse four words.

**Total original K04 SHA256 checks: `12,288 × 624 × 8 = 61,341,696`.** All were performed in six independent, mutually disjoint contiguous layout ranges, each with exactly **10,223,616** source-derived complete candidates and zero original commitment matches. The six executed layout ranges were [1,2049), [2049,4097), [4097,6145), [6145,8193), [8193,10241), and [10241,12289). Every run asserted the same 12,288-layout space and its exact per-range comparison counter. No source file or verifier was changed.

## Controls, portability, and limits

The script checks 100 temper/untemper word roundtrips and **predicts an entirely held-out four-output block of a seeded real Python `random.Random(1300199)` MT generator exactly** from 624 known original-shaped outputs, before the real source search. This validates the actual MT recurrence and quotient method; it does not show any shared historical generator. Original file hashes, selected job identity, accepted K01/K06 components and route/commitment are pinned.

[Portable standard-library single-file SFT](../agents/agent8/k04_mt624_cyclic_source_sft.py) reads repository `resources/`, supports layout ranges via `--start` and `--stop`, and is byte-identical to the local portable reproduction, Git blob `f0c75200db53ca0aaa4c8fe8b082dc1800e39256` and SHA256 `f1f58b6d6da52a1487bc66a2d1492655e419cf9daa14cad6feaf0b35e92cf287`. A separate local path-adapted variant ran all six complete source ranges, each reporting `original_hits=[]`. A portable two-layout test passed source assertions and comparison count before committing.

**Scope:** Excludes only this rotated, untempered, whole-source-state, one-twist publisher with these 12,288 group layouts and eight serializers. Source chronology makes a single physical shared emitter doubtful, particularly given recorder observations later than the selected coupon. This is a speculative complete-candidate construction, neither a recovered physical K04 byte nor a K08 final word. Further blind phase/seed expansion without independent source-bound stage selection is a poor substitute for the original escrow coupon or exact final Emily inscription.
