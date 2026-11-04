# K04: complete two-leading-byte plus arbitrary nonadjacent two-byte copier repair, 335 billion original checks

**Agent 7 | 4 November 2026 | Original-source-pinned complete result.** This is a novel, narrowly defined K04 four-whole-byte support family and a source-bound search. The authentic original physical selected ACK2 coupon remains unknown, K04 stays MISSING, and six other original REC8/1 slots remain PASS; K08 is independently unresolved.

## Concrete new candidate mechanism

The selected historical printer event is `ESC-N → PS-261003-0417, 2026-10-03T18:02:00Z, ATTEMPT=2 STATE=ACK CLASS=RECOVER DEST=bench`. Its copied unverified 16-byte RECOVER payload is `A9A9DC5731A5E2AE879C47215C2559D5`, the fixed commissioning XOR mask is `8556C8CB6140A7F9A5123AC7571BEE1C`, and copied reduced component is `2CFF149C50E54557228E7DE60B3EB7C9`. The unchanged original K04 SHA256 acceptance commitment is `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`.

Prior exhaustive original-target studies ruled out any replacement of no more than three *arbitrary whole bytes*. [Agent19's complete source-pinned 4-byte paired-burst result](h17-k04-selected-a9a9-plus-second-two-byte-burst-20261104.md) held copied byte locations0,1 as arbitrarily wrong and placed the other two arbitrary faults in adjacent locations j,j+1, **j=3..14**, with the j=2 contiguous-four-byte case already previously excluded. The fixed leading duplicate `A9A9` gives a conditional physical-capture hypothesis, although its anomaly is weak, as Agent19 correctly notes.

**New candidate family:** keep byte locations0 and1 arbitrary, and set the other two arbitrary byte locations to any **nonadjacent** pair (i,j), where 2 <= i < j <= 15 and j >= i+2. Keep the other 12 bytes *identical to the copied payload*. The exact positions are 78 unique supports, disjoint from the previous adjacent second-pair supports. Each of the four bytes is independently assigned all 0..255 values, including values identical to the copied value; therefore each support spans exactly **2^32** complete candidates. It is equivalent to applying all corresponding physical copier repairs then XOR-reducing the route, since XOR with the fixed mask is bijective byte by byte.

**Total genuinely new complete original K04 SHA256 checks: 78 × 4,294,967,296 = 335,007,449,088. Result: zero original commitment matches.**

This closes the specific *leading two arbitrary bytes plus exactly two further arbitrary bytes anywhere* fault family, combining the earlier 13 adjacent supports with these 78 nonadjacent supports. It excludes a **91-support** (C(14,2)) four-byte position class, under the stated intact remaining 12 bytes premise. The prior tests and this one may share some *candidate byte strings* where a nominated changed byte coincides with its copied value; the 78 position supports themselves are distinct and the new test is exhaustive for each.

## Original-source controls and complete remote execution

The [single-file reproducible C++17/OpenSSL/OpenMP solver](../agents/agent7/k04_a9a9_nonadjacent_fourbyte_sft.cpp) imports the audited Agent8 optimized single-block SHA256 verifier but enumerates **all 78 previously untested supports** and performs independent full-content input checks:

- Unmodified original spool SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`, plus unique full literal selected ACK2 record;
- Original recovery-route 16-byte XOR mask;
- Original acceptance K04 full SHA256 commitment;
- One-thousand changing inputs checked against ordinary OpenSSL SHA256 and single-block `SHA256_Transform` exactly;
- **A separate complete planted synthetic target for every one of 78 four-byte position supports**, with arbitrarily changed source-component bytes `DE AD BE EF`. The *actual exhaustive same-candidate loop* must recover that planted target **exactly once per support**.

The [manual 16-shard workflow](../.github/workflows/agent7-k04-a9a9-nonadjacent-manual.yml), [completed source-pinned original run 41837544940](https://github.com/FlareZ123/workplace-v2/actions/runs/41837544940), partitions supports by rank modulo16. All **16/16** individual jobs returned `conclusion=success`, with each completed shard confirming its exact support count, 2^32 full SHA256 comparisons per support, zero original matches, and one planted positive per support. A representative concrete job (shard10, run job126600266617) reports five complete supports (10,26,42,58,74) and:

```text
PAIR_DONE pair=10 index2=2 index3=14 candidates=4294967296 original_hits=0 positive=1
...
PAIR_DONE pair=74 index2=11 index3=15 candidates=4294967296 original_hits=0 positive=1
SHARD_COMPLETE shard=10 pairs=5 complete_checks=21474836480 original_hits=0 planted=5 secs=256.107
```

Each of the 78 selected candidate supports appears in precisely one shard; no unordered support is omitted or duplicated. Since source and printer files were read-only and all shards succeeded with matching counts and planted-positive assertions, the output is a meaningful complete conditional finite exclusion, while it does not certify the actual historical physical fault mechanism.

## Larger follow-on: remaining independent four-byte-position frontier, IN PROGRESS

The results leave **1,713 previously unexhausted unordered four-byte support patterns** out of all C(16,4)=1,820 possible supports, after excluding:

- 91 head-pair supports just completed (13 earlier adjacent, 78 new nonadjacent);
- 12 *other* contiguous four-byte windows that were completed in inherited workplace-v1;
- Four same-lane one-byte-per-32-bit-word supports fully excluded in [Agent19's independent common-lane search](h17-k04-four-word-correlated-byte-lane-20261104.md).

A follow-on [single-file complete-support SFT](../agents/agent7/k04_remaining_fourbyte_supports_sft.cpp) enumerates exactly these **1,713** remaining supports, each with 2^32 independent replacements. It asserts the original source and original target, uses a separate planted full target per support, and is partitioned into **128 disjoint CI shards**. The [single-job source/synthetic preflight](https://github.com/FlareZ123/workplace-v2/actions/runs/41838264323) passed, including all 1,713 planted SHA controls. The [full computation was dispatched as run 41838591961](https://github.com/FlareZ123/workplace-v2/actions/runs/41838591961), but **its 7,357,278,978,048 planned original SHA256 checks are NOT part of this report's completed negative result**. Do not claim a five-byte Hamming bound, complete 1,820-four-byte sweep, or K04 recovery until the 128 individual full-search jobs and complete counters have been reconciled. If any original match appears in a job log, preserve the full printed component and verify the unmodified original checker before making a recovery claim.

The archived files and canonical accepted candidate were never changed.

**Conclusion:** The new 335-billion search excludes the entire remaining conditional two-leading-byte-plus-two-other-byte repair family. **No original K04 bit is authenticated.** The broader complete 4-byte-position experiment is a pending independent probe, and K08's original final handwritten wording is still missing.
