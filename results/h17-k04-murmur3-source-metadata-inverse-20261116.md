# K04: exact inverse of MurmurHash3 128-bit metadata issuers (16 November 2026)

**Agent 22. Original source gate: zero 32-bit-seed initializers in 1,552,320 complete source-output comparisons. No selected K04 coupon, key byte, or new REC8/1 PASS recovered.** This is a new candidate issuer model, distinct from the older Murmur64-based V8 state seeding result. The six previously accepted components are unchanged; K04/K08 remain missing.

## Source-linked hypothesis

The 133 retained print-spool rows each contain a 16-byte opaque payload plus a job ID, attempt, state, class, destination and timestamp. A potential issuer architecture is a 128-bit MurmurHash3 fingerprint of canonical job metadata, with a shared **unknown 32-bit unsigned seed**, rather than a multistage random stream. If a metadata serializer and 32-bit seed explain intact historical source packets, the same producer can output a complete selected PS-261003-0417 attempt-2 coupon without using its suspect copied bytes.

This is exploratory: MAIL-16 and the routing record explicitly call the coupon bytes opaque. Neither source states that a MurmurHash issuer was installed, nor that a job's text fields were hashed. The ordinary spool rows are copied fragments, without native media checksums. Accordingly an exact fit on independently copied records would be a conditional producer result, and the lack of one excludes only the specified metadata-hash models.

## Analytical inversion instead of seed brute force

The standard MurmurHash3 x64_128 and x86_128 algorithms initialize all 64-bit or all 32-bit state lanes to one unsigned 32-bit seed. For **known input bytes** and a full 16-byte output, their final XOR-shift, odd-multiplier, rotation and modular-addition operations can all be inverted in exact reverse order. This yields the **unique initial internal state** for that candidate input and output. A valid standard-issuer output must have identical recovered lanes and, in the x64 variant, both lanes no greater than 0xFFFFFFFF.

For x64 the output final additions invert by letting B = out2 - out1 and A = out1 - B modulo 2^64. Undo each fmix64 with modular multiplicative inverses, undo the preceding paired additions and length XOR, undo the tail word mixes, then reverse every 16-byte block. For x86 the four-lane final additions and fmix32 operations invert similarly; reverse the four block mixes in lane order 4,3,2,1. All candidate strings and outputs have the same lengths as source. This mathematical inversion tests an entire 2^32 seed space per input/output comparison at constant computational cost.

Authority for the algorithm: [Austin Appleby's public-domain SMHasher MurmurHash3.cpp](https://github.com/aappleby/smhasher/blob/master/src/MurmurHash3.cpp). An independent installed Cython native MurmurHash implementation was invoked for 100 sampled input lengths and seeds in **each variant**; both Python forward and inverse paths agreed exactly in all 200 cases.

## Frozen input and complete source test

- Original spool file SHA-256: 7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083.
- Exactly **132** retained nonselected payloads are used, including the 128 ordinary ACK rows and four exceptional rows. The **18:02 selected ACK2 copied payload, row129, is excluded** from all seed inference.
- **30** source-derived metadata input formats per row cover the exact job ID, job plus attempt, job/class/destination combinations, literal JOB/ATTEMPT/STATE/CLASS/DEST fields, timestamp-containing layouts, and relevant suffix views. The actual finite strings are defined in the reproducer. No arbitrary wordlist, hidden source, K04 hash-fitting or invented source field is used.
- For x64_128, both 64-bit lane orders with independent per-lane endian choices: **8** byte layouts. For x86_128, all 24 orders of four 32-bit lanes and independent 16 lane endian choices: **384** byte layouts.
- Complete exact checks: **132 × 30 × 8 = 31,680** x64 inversions and **132 × 30 × 384 = 1,520,640** x86 inversions; **1,552,320** total.

| Historical source gate | Full comparisons | Valid unsigned 32-bit initialized outputs |
| --- | ---: | ---: |
| MurmurHash3_x64_128 | 31,680 | **0** |
| MurmurHash3_x86_128 | 1,520,640 | **0** |
| **Total** | **1,552,320** | **0** |

Reference fixtures from the independent native implementation include x64 hash of UTF-8 `Hello` at seed0, in in-memory byte order, `1cc4d455ff74b93544551229cfea00a0`, and x86 `46ae6023c636635ef4b345adf4b345ad`. For source-shaped test messages `PS-261003-0300|1`, seed0xDEADBEEF, x64 is `3b9d214972520191aa7fc4cffe50f7a0` and x86 is `f79fc8eba9c28ed43a06c84a253f85ec`. Both variants passed their independent planted full-output fixtures and recovered a planted shared 32-bit issuer seed from two genuine-format donor messages to predict the complete selected-job output and its XOR-masked synthetic component.

## Reproducible artifact and decision

The standalone standard-library Python [SFT](../agents/agent22/k04_murmur128_inverse_source_sft.py) pins the exact spool content, parses its 133 jobs, validates the selected row identity, implements the full inverse/forward path, exercises independent published/native fixtures and the two-donor selected-job positive, then performs every source-output comparison above. Run from the repository root with Python 3. Input files, official candidate, original acceptance and verifier are read-only.

The original source does not support either standard MurmurHash3 128-bit metadata emitter in the 30 declared input formats and common byte layouts. No seed survives even **one** exact nonselected output, so no model is promoted to a K04 coupon candidate or original K04 hash comparison. The negative does not cover nonstandard variants, unknown metadata encodings, another fingerprint family, or an independently generated physical paper value. Further unanchored hash-name enumeration would have little justification without a native printer-issuer clue.

**REC8/1 status unchanged:** K01/K02/K03/K05/K06/K07 PASS. K04/K08 MISSING. Combined INCOMPLETE.

## Independent GitHub Actions replay (16 November, 13:19–13:20 UTC)

The repository-committed Python reproducer was executed directly against the unchanged original `resources/` checkout in [manual GitHub Actions run 43874690015](https://github.com/FlareZ123/workplace-v2/actions/runs/43874690015). **Job source_inverse completed SUCCESS**, with the exact end markers:

```text
INDEPENDENT_REFERENCE_FIXTURES=PASS TWO_DONORS_TO_SELECTED_PLANTED=PASS
ORIGINAL_SOURCE_GATE x64_128 checks 31680 initializer_matches 0
ORIGINAL_SOURCE_GATE x86_128 checks 1520640 initializer_matches 0
SOURCE_GATE_COMPLETE
```

This confirms the persisted implementation, its complete declared original-source search, and both positive controls. It does not extend the finite exclusions beyond the reported metadata serializer and byte-view choices. The single-use workflow definition was subsequently retired; the completed run and retained script remain the reproducible evidence.

## Predecessor correction: expanded source gate, shared algorithm (16 November)

The **MurmurHash3 inverse itself is prior art**. Agent 39 had already implemented exact x64_128 and x86_128 arbitrary-initial-state inverse models and reported **zero standard equal-lane 32-bit seed initializers** under **24 metadata formats × 8 views**; see [4 November full-128 Murmur report](h17-k04-murmur128-unknownstate-inverse-heldout-20261104.md). Agent 13 had separately inverted x86_128 across selected K01/K02/K05/K06/K07 record labels, also finding zero standard scalar seeds; see [cross-archive x86 test](h17-k04-crossarchive-murmur3-x86-native-20261104.md). Those reports precede this run and must be treated as the discovery of this technique.

**Exact incremental scope here:** 30 alternative input serializations for **all 132 unselected printer records**, including strings that overlap the predecessor's 24; for x64, the eight familiar 64-bit byte views; for x86, all **24** four-word orders and **16** independent word-endian configurations rather than the earlier eight selected views. The complete 1,552,320 zero-match source initializer tests expand a **previously source-incompatible standard-scalar-seed hypothesis**. They do not independently establish a new printer mechanism, nor add selected K04 value information. The completed remote check validates the extended implementation; avoid rebuilding the same inverse/seed screen under another variant spelling.
