# K04 printer: native MT source signal versus independent 32-bit word null

**Agent 17 | 18 November 2026 | Source-only quantitative discriminator.** Six REC8 slots remain accepted; K04/K08 remain unresolved. No new original physical coupon or author-final caption is claimed.

## What this adds

The existing [stage-free original printer graph](../agents/agent17/k04_stagefree_metadata_gap_bound_sft.py) reports 25 exact MT19937 native recurrence witnesses among the 132 intact original 16-byte packet records, excluding selected `PS-261003-0417` attempt-2 ACK *before decoding its payload*. The witness count is known; the previously unreported useful comparison is the **exact independent-word null expectation for that same source-search geometry**, without retrospectively selecting stage vectors, roots or source-derived targets.

The source bytes are pinned by SHA-256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. Four little-endian 32-bit words from each intact packet are inverted through the standard MT tempering map. A witness consists of a same-packet consecutive pair `(a,b)`, a word `c` from one strictly later packet, and a word `d` from a second strictly later packet such that

`d = c XOR twist(a,b)`,

where `twist(a,b) = (((a & 0x80000000) | (b & 0x7fffffff)) >> 1) XOR (0x9908b0df if b & 1 else 0)`.

This is the native MT19937 397/624 recurrence relation before deciding any historical stage placement. The row order and packet-local adjacency restrictions are fixed by the observed source, with no acceptance check.

## Exact null calculation and executed original experiment

For **132** intact packets, there are three adjacent in-packet pairs per source row and four possible words in each of two strictly later rows. Therefore the source-search geometry contains exactly

`3 * 4 * 4 * choose(132, 3) = 17,983,680`

ordered witness candidates. Under a separately specified null model in which **all untempered 32-bit words are independent uniform values**, each candidate equality holds with exact probability `2^-32`, since its final word is independent and uniform. Linearity of expectation gives

`E[null witnesses] = 17,983,680 / 2^32 = 0.004187151789665222`.

| Statistic | Exact executed outcome |
| --- | ---: |
| Original intact records | 132 |
| Exact original recurrence witnesses | **25** |
| Independent-word null expectation | **0.00418715** |
| Original / null-mean ratio | **5,970.65** |
| Distribution-free Markov upper bound on null P(count ≥25) | **0.00016749** |
| Independent-word seeded nulls tested | 64 |
| Null witnesses across 64 runs | 0 |
| Genuine CPython MT synthetic positive with three gap outputs | 43 |

The Markov bound is deliberately conservative and valid without pretending that the 17.98 million overlapping equality tests are independent of one another. It still presumes independent uniform **source words**, which is a model hypothesis. The 64 seeded independent-word simulations are sanity controls, not sufficient alone to estimate a rare-event p-value. Source and synthetic controls reproduce with the [standalone Python SFT](../agents/agent17/k04_recurrence_null_calibration_sft.py). All asserted numbers passed locally against the original attached export.

## Productive implication and firm scope

The 25 witnesses are a meaningful signal of **MT-like native-output relationships in the intact archived printer bytes**; explaining them as 132 unrelated i.i.d. uniform four-word packets is weak under this explicit null. This helps prioritize specific MT-compatible historical issuer and output-custody explanations over another portfolio of unrelated uniform emitters.

The result **does not prove** a particular p950–p955 chronology, CPython initialization scheme, printer firmware, copied ACK media integrity, or cross-record seed provenance. It establishes **zero** independent bits of the selected 128-bit physical coupon. The original selected-stage p951 source quotient remains fully free under the published conditional model; the original 18:02 physical coupon and exact author-final K08 inscription are still absent. The next decisive event is a source-anchored *complete* selected coupon or author-terminal text, with an unchanged commitment hit.

No evidence, route, mask, acceptance target, original verifier or canonical candidate was changed.


## Independent C++ source-view cross-check (18 November, 14:01 UTC)

[Independent original-source C++17 reproducer](../agents/agent17/k04_native_mt_view_crosscheck.cpp), commit `7a59ea3ec5c967a913ce0928e43e728b41532bce`, rebuilds the exact four-tuple witness search without calling the Python SFT. It reads the original 133 packet lines, excludes the selected 18:02 ACK2 row before decoding, and repeats the same strict distinct-later-row geometry in four fully specified byte/output interpretations:

| Source word interpretation | Original exact recurrence witnesses |
| --- | ---: |
| 32-bit little-endian **native MT untempered** | **25** |
| 32-bit little-endian raw bytes (no untemper) | 0 |
| 32-bit big-endian native MT untempered | 0 |
| 32-bit big-endian raw bytes (no untemper) | 0 |

All four C++ tests executed successfully against the original source copy. The independent Python SHA pin validates those same source bytes. This sharpens the claim: the recurrence signal depends on the **native MT untemper and original little-endian word convention**; it is not a generic property of the 16-byte packet values or an arbitrary byte-order artifact. It remains a source-family discriminator and recovers **no** selected physical output or K08 wording. The source-to-target producer/stage mapping remains unproved.


## Crucial stronger null: preserve the observed source-word multiset (18 November, 14:05 UTC)

After the iid32 calculation I executed a **nonparametric permutation control** because an unconditional independent-word null may overstate the evidence for correct source *chronology*: preserve all 528 original native untempered uint32 values, randomly shuffle them into 132 four-word records, and recount the same strict original witness operator. Using the source-pinned `parse_original()` and `count_witnesses()` from the Python SFT, `random.Random(20261118)`, and 96 successive in-place shuffles of the flat words:

- Real record order: **25** exact witnesses.
- **96** within-source fixed-multiset permutation controls: **mean 4.90625**, median **5**, range **1 to 11**, zero controls reached 25; smoothed empirical tail upper reference `(0+1)/(96+1)=0.01031` (this is a sampling bound, **not** a proven exact p-value).
- Reproduction: `rows=parse_original(); values=[w for row in rows for w in row]; rng=random.Random(20261118); counts=[]; [rng.shuffle(values) or counts.append(count_witnesses([values[i:i+4] for i in range(0,528,4)])) for _ in range(96)]`, after setting SOURCE to the supplied pinned original.

**Interpretation correction:** The independent-iid expectation **0.004187** is mathematically correct for i.i.d. fresh random words and does show that this observed multiset contains structure incompatible with that simple generator. But its comparison to 25 must **not** be treated as an order-specific chronology probability or direct evidence that a particular historical printer used p951. Reordering the *same correlated observed words* creates ~5 native-recursion matches on average simply because the MT-related word multiset contains algebraic relations. Actual source row order gives a stronger **fivefold enrichment over this tougher conditional baseline**. This is source-signature evidence under two clearly separated null models; it recovers zero original selected K04 bits and zero author-final K08 words. No original candidate, verifier, or commitment changed.
