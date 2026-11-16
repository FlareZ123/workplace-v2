# K08 12-word / motif-mask!=7 bigram search — shard [127,331)

**Status:** completed, exact coverage of this disjoint shard, no original-target hit.

## Scope

This run covers all directed 12-word paths in the pinned source-bigram graph whose motif mask is not 7, with first-word IDs in the half-open range [127,331). Motif bits are: bit 0 = sea/water, bit 1 = night/watch/morning, bit 2 = table/voices/room.

The source graph is built from N01–N24, MAIL11, and MAIL20 using the shared extraction, tokenization, obsolete-label removal, and signature truncation rules. The executable pins the SHA-256 of each of the three source files. It reproduced 26 source records, 331 distinct words, and 570 unique directed bigrams.

## Method

- C++17, OpenSSL SHA-256, OpenMP with 4 threads.
- For each candidate, normalize is the source graph's lowercase ASCII alphanumeric token sequence joined by single spaces.
- Compute HMAC-SHA256 using the K08 desk nonce as key; take the first 16 bytes; SHA-256 those 16 bytes; compare to the original K08 acceptance commitment.
- Search only exact length 12 and mask != 7. This is the unsearched region identified by the Critic's preflight; previously searched lengths and mask-7 paths are not repeated.
- Reproducible runner: [agents/agent1/k08_bigram_filtered_shard_sft.cpp](../agents/agent1/k08_bigram_filtered_shard_sft.cpp).

## Result

Run started 2026-11-16T07:41:10.502Z and ended 2026-11-16T07:43:20.811Z.

```
K08_BIGRAM_FILTERED_12_MASK_NE_7
start_begin=127
start_end=331
source_records=26
words=331
edges=570
max_words=12
checked=918492697
planted=0
original_hits=0
EXIT_CODE=0
```

The checked count exactly matches the independent dynamic-programming oracle for this shard: **918,492,697**. The N03 synthetic control starts at word ID 22 and is intentionally outside this shard, so the expected planted count here is **0**. The runner passed its source pins, graph checks, N03 HMAC/commitment self-test, shard count assertion, and synthetic-count assertion.

## Interpretation and remaining coverage

This shard contributes **918,492,697 / 1,822,326,388** candidates in the newly identified region. It found no K08 commitment match.

The disjoint Agent18 shard is [0,127), expected **903,833,691** candidates, and contains the N03 positive-control start word ID 22. Until that shard reports its exact checked count, synthetic count 1, and original-target result, the full 12-word/mask!=7 region is **not** complete. Do not report a whole-region negative yet.

Even after both shards complete, this only excludes the specified 12-word paths in the conditional lexical bigram graph; it does not prove the final phrase cannot use another length or a different source/version construction.
