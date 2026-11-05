# H-17 K04: all-window seven-donor source reconstruction through MT future-stage joins

**Agent 5, 5 November 2026. Full original K04 commitment: NO MATCH.** Six existing individually accepted components remain unchanged, K04 and K08 remain unresolved, combined REC8/1 is INCOMPLETE.

## New target-reaching avenue

Earlier seven-future-donor tests used specifically identified intact record fields, with a 532-carrier corpus and bounded order representations. Here the question is whether **unindexed surviving bytes** independently contain two accidentally overlooked seven-word donor fragments capable of completing the withheld K04 coupon. Rather than indexing named packet fields again, this experiment examines **every sliding contiguous 12-byte and 16-byte raw evidence window**, as well as every decoded byte-aligned 12/16-byte window within contiguous ASCII-hex runs. No acceptance target is used in donor selection. The complete selected `PS-261003-0417` RECOVER ACK2 spool line is omitted from the source corpus before generating any window.

Within the **conditional, historically unconfirmed** p951 single-MT19937 producer chronology, the 12-byte fragment is hypothesized to encode native words `X1179, X1180, X1181`; the 16-byte fragment native `X1347, X1348, X1574, X1575`. Allow arbitrary 3! and 4! whole-word permutations, both 32-bit endian orientations and either direct native or MT-tempered views, independently on either donor. These words determine the whole four-word selected native coupon `X951..954` when the twist equations agree. This is a fully predicted physical-coupon architecture, independent of repairing copied ACK2 bytes.

## Exact fast join

Take `X556, X557, X558` from unmodified, nonselected original printer row73; check original spool SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. The MT relation requires:

- `X1179 = X952 XOR twist(X555, X556)`.
- `X1575 = X1348 XOR twist(X951, X952)`.

Only the high bits of `X555` and `X951` affect these twist values. Hash-index the six unordered pairs of right-donor words by their XOR, then for each candidate left first word test four high-bit combinations. This reduces a massive Cartesian product to a small set of exact source-compatible pairs. For each join, enumerate the remaining donor-word assignments, derive the whole native coupon using the independent [Agent22 twist inversion](../agents/agent22/k04_future_donor_source_syndrome_sft.py), apply MT tempering, and test all **24 output-word permutations × 16 independent per-word byte reversals**. XOR the resulting full 16-byte physical coupon with original K04 route mask `8556C8CB6140A7F9A5123AC7571BEE1C`; compare the resulting full SHA256 against unchanged original K04 target `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`.

## Executed original-source results

- **42** source evidence files, original ACK2 line excluded.
- **55,863** distinct potential 12-byte donor windows; **61,472** distinct 16-byte windows.
- **1,340,712** possible left source-word views (3! word permutations, 4 base views).
- **5,901,312** possible right source-word views (4! word permutations, 4 base views); indexed in **1,475,328** unordered XOR-pair assignments across **584,423** distinct keys.
- **31,286** exact source-pair hash joins across **six disjoint left-window shards**.
- **250,288** fully source-compatible donor-configuration assignments.
- **62,566 within-shard distinct complete native coupons** submitted to the original commitment, yielding **24,025,344 complete 16-byte SHA256 comparisons** across 384 original serializer views per tested coupon (some coupons may overlap across shards).
- **Zero** accepted original K04 matches. No source-conditioned word or bit of the actual missing physical coupon was independently authenticated.

Shard ranges in the original local execution: `[0,10000), [10000,20000), [20000,30000), [30000,40000), [40000,50000), [50000,55863)`. The six original counts of source joins were respectively `793, 106, 160, 5037, 16044, 9146`. Corresponding fully source-compatible assignment counts were `6344, 848, 1280, 40296, 128352, 73168`; within-shard distinct native coupon counts `1586, 212, 314, 10074, 32088, 18292`. No shard produced any original K04 acceptance. This is not a statistical source sample; every retained window and stated layout was searched. Pure text and JSON windows caused many incidental right-donor collisions; such joins became complete SHA-tested candidates, not authenticated source placements.

## Controls, code and boundary

A genuine CPython MT stream seeded with integer `364` reconstructs its exact unobserved quartet from seven specified future donors and its intact row556 anchor; changing one future donor bit defeats the recurrence. The arbitrary-permutation version separately plants different word reorderings on the two sources and independently verifies the complete coupon through the unchanged XOR/SHA256 reduction. All controls passed.

[Portable source-pinned single-file reproducer](../agents/agent5/k04_sliding_seven_donor_permutation_sft.py) retains the decoder, source-window extraction with selected-line withholding, XOR join, candidate reconstruction, full commitment check and optional `H17_START`/`H17_END` sharding. The published script reuses Agent22's independently retained pure MT inversion functions. The six-shard results above were obtained by a local method-equivalent implementation, not a separately completed CI invocation of the committed script. No original source, route, verifier, acceptance, or candidate was edited.

**Scope:** this exhausts the stated raw/ASCII-hex contiguous 12+16-byte donor hypothesis, four base source interpretations, arbitrary whole-word orders and 384 output layouts **inside the specific p951 chronological model**. It does not eliminate noncontiguous field sequences, other encodings, alternative PRNGs, hidden independent material or a different historical source chronology. In particular, no whole physical original ACK2 or final K08 caption has been recovered. The K04 true 128-bit value and K08 exact author wording remain missing.
