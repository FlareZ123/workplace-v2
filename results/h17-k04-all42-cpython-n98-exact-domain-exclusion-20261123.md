# K04: exact partial-triple domains exclude all 98-word CPython seeds under the all42 source chronology

**Agent 1 | 23 November 2026 | New finite source-inversion constraint, genuine-seed positive controls passed; K04 still unknown.**

## New mechanism

Agent50's all42 source-consistent native MT chronology supplied **528** intact 32-bit original printer outputs and source rank **15,434** over the 19,968-bit initial MT state. Its real-output-offset scan of genuine CPython `random.Random(integer_seed)` left **29 necessary-compatible offsets** for the smallest surviving 98-word seed length. The accompanying key-residue inversion had at least 70 entirely unobserved seed words, and could not construct an actual source seed.

That inversion observed a CPython `init_by_array` key term only when the three consecutive initialized state words were known with at most one free bit apiece. This experiment instead expands **every exactly determined masked three-word domain with up to 16 unknown bits total**. For each offset and `i = 4..623`, given compatible `(S[i-2], S[i-1], S[i])`, compute the exact 32-bit key term:

```text
A = ((S[i-1] + i - 1) mod 2^32) XOR [1566083941 * (S[i-2] XOR (S[i-2] >> 30)) mod 2^32]
B = ((S[i] + i) mod 2^32) XOR [1566083941 * (S[i-1] XOR (S[i-1] >> 30)) mod 2^32]
T[i] = B - (G[i] XOR [1664525 * (A XOR (A >> 30)) mod 2^32]) mod 2^32
```

where `G` is the documented CPython seed initializer from scalar **19650218**. The same genuine seed word must equal every `T[i]` with matching residue `(i-1) mod 98`. The test takes **exact finite set intersections** of all locally permitted key terms for that residue. Any empty intersection rejects that seed length and actual output offset, without assigning a seed, consulting selected ACK2, or relying on a hash hit. The 16-free-bit cutoff is a conservative superset constraint: every genuine source-fitting seed must occur in its enumerated domains.

## Original-source result

- Original `spool-reconstruction.log` SHA-256 checked: `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`.
- The selected **18:02Z PS-261003-0417 attempt2 RECOVER ACK** row129 is excluded before its disputed payload is decoded. All 132 other original rows are retained; all 624 actual prior-output offsets are tested.
- The baseline 1-bit-total triple screen reproduces exactly **29** necessary-compatible offsets for a 98-word seed: `586,587,588,589,590,593,595,596,597,598,599,600,601,602,603,604,605,606,607,608,609,612,613,615,616,618,619,620,621`.
- **The exact extended 16-free-bit domains contradict every one of those 29 offsets.** None can come from a genuine 98-word CPython integer seed under the frozen all42 chronology.
- Example offset **616**: the fully determined `i=25` key residue 24 conflicts with all **65,536** possible three-word completions at `i=221`, whose key term has the same residue `(221-1)%98 = 24`. This is a complete finite contradiction, irrespective of the 70 otherwise unseen seed words.
- Two genuine 98-word Python-seeded MT histories at actual output offsets **0 and 616**, retaining the identical original row-stage schedule and erasing their selected row129, both pass the baseline and extended source compatibility tests. All four planted controls preserve the source-derived 624-word state masks and correctly retain the true seed term. Thus the filter does not discard an actually seeded 98-word source.

**Conditional strengthened bound:** prior original-source work rejected seed lengths 1..97 for all source-compatible origins; adding this all-origin result rejects 98 as well, so a genuine CPython integer seed compatible with the exact all42 model must contain **at least 99 32-bit words**, assuming `init_by_array` is the producer and the stage schedule is correct.

The actual historical print writer, seed length, state chronology and selected physical coupon remain unauthenticated. This finding is a strictly conditional **source-producer exclusion** and **does not recover K04 bytes**. Original K08 and combined REC8 remain incomplete.

## Reproduce and next step

[Standalone source-pinned single-file test](../agents/agent1/k04_all42_cpython_n98_extended_sft.py). Executed against the unmodified supplied ZIP and passed genuine seeded controls, original-source rank, all 624 origin tests, 29 original eliminations and final assertions.

The useful extension is a **predeclared 99–128-word seed-length batch**, caching the exact local domains per source origin so repeated key residue tests are cheap; avoid further speculative nested source-proof variants that do not reach a source-authenticated coupon. Original source, `resources/verify.py`, acceptance commitments and canonical six-slot candidate unchanged.
