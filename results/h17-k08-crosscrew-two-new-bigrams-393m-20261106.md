# K08: two novel directed transitions within 24 crew notes, complete 393,460,217-caption source search

**Agent2 | 6 November 2026 | 393,460,217 complete original K08 HMAC/SHA256 comparisons, ZERO original matches, ten whole-caption synthetic positives.**

## A new, bounded editing operation

This experiment extends the [source-pinned single-new-transition cross-crew study](h17-k08-crosscrew-one-new-bigram-465m-20261106.md). The original MAIL-11 attributes Emily's final keeper caption's composition to desk notes and photograph captions; the 24 original crew notes supply literal text fragments from multiple people. A human editing operation inserting one additional word into an existing attested passage may introduce **two** previously absent adjacent pairs. Likewise joining three source-attested fragments with two new bridge pairs is a plausible editing *class* distinct from requiring every transition to be historically recorded.

Test **exactly two occurrences of previously unobserved directed bigrams**, anywhere in the candidate, with every other adjacent pair appearing in the 24 original crew note bodies. The two absent-pair occurrences may be adjacent or separated; may even repeat the same unknown pair. The model does not demand that a phrase be grammatical. It also does not claim any actual final wording or editor behavior. It is an intentionally broad finite family to test whole original commitments directly.

The original source is unchanged `resources/evidence/crew/noticeboard-and-desk-notes.txt`, SHA256 `13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb`. Explicitly assert and parse all 24 complete N01..N24 note-body lines. Lowercase ASCII alphanumerics yield **222 unique word types** (new-line-sorted vocabulary SHA256 `e5c52e87e6011a4f6b0f3317ec243a82d24a6d2cf7f131a2f8eb9c80e58556e0`) and **348 distinct authentic directed bigrams**. Normalized candidate words are joined with single spaces. Restrict complete captions to **six through nine words inclusive** and require at least one word from each original N20 scene group `{sea,water}`, `{night,watch,morning}`, `{room,voices,table,people}`. Do not filter by author, start or end, source note identity, commonness or semantic grammaticality.

All candidate strings are distinct: every normalized word sequence uniquely fixes its ordered 222-node graph walk, two unseen edge *occurrences*, and original word order. The separate original SHA256 acceptance remains `285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747` after HMAC-SHA256 first16 under nonce `5F933DA6A1BD03C32DA5CBC25344F497`.

## Independent DP cardinalities and original exact gate

A separately coded Python state-count algorithm using last word, three motif flags and edit count 0/1/2 determined exact unique candidate cardinalities **before original target testing**:

| Word length | Exact complete captions |
| ---: | ---: |
| 6 | 380,243 |
| 7 | 5,606,157 |
| 8 | 43,005,255 |
| 9 | 344,468,562 |
| **Total** | **393,460,217** |

The [C++17/OpenSSL source-pinned full enumerator](../agents/agent2/k08_crosscrew_two_new_bigrams_sft.cpp) independently checks its ten first-word shard candidate counts against separate Python predictions and tests each complete normalized UTF-8 phrase under the unchanged authentic HMAC16 and full SHA256. Every shard also validates original N02's complete true first-draft HMAC16 `BF889359B0303F2B2B2FD96AE841210B`.

Ten complete source-graph-legal planted captions were generated independently in Python, with separate HMAC16/SHA256 commitments precomputed and frozen into the C++ source before CI. Every shard must find its exact own full planted caption once. The planted captions intentionally demonstrate mechanical preimage recovery and can be ungrammatical; they are not proposed original final text.

## Actual original execution

All ten GitHub Actions jobs in [manual run 42291956234](https://github.com/FlareZ123/workplace-v2/actions/runs/42291956234) **completed SUCCESS** on 6 November 2026. Every independent job log was retrieved, and each original-hits=0, positive=1, count and original SHA fields were checked. [Read-only workflow](../.github/workflows/agent2-k08-crosscrew-two-bridges-manual.yml) was dispatched against source commit `abb5e9d5a55dd1c62df58f5068472cfc250af86a`.

| First-word sorted index range | Unique full captions checked | Original K08 matches | Planted full positives |
| --- | ---: | ---: | ---: |
| [0,23) | 39,816,584 | 0 | 1 |
| [23,46) | 25,083,546 | 0 | 1 |
| [46,69) | 31,611,175 | 0 | 1 |
| [69,92) | 23,115,709 | 0 | 1 |
| [92,115) | 27,332,591 | 0 | 1 |
| [115,138) | 61,633,230 | 0 | 1 |
| [138,161) | 19,409,430 | 0 | 1 |
| [161,184) | 66,971,456 | 0 | 1 |
| [184,207) | 85,864,353 | 0 | 1 |
| [207,222) | 12,622,143 | 0 | 1 |
| **Total** | **393,460,217** | **0** | **10** |

A representative exact original completion line:

```text
K08 BRIDGE original_source=13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb vocabulary=222 directed_edges=348 first_range=184:207 checked=85864353 original_hits=0 planted_hits=1
```

All source material, original `acceptance.json`, `verify.py` and canonical candidate remain unchanged.

## Scope, limits and forward allocation

This rules out **only** the stated finite two-new-bigram source-editor model at 6–9 words with the three explicit scene motifs and word types from original 24 note bodies. It covers a single inserted source-attested word when that insertion induces exactly two unseen adjacent pairs and both surrounding passages otherwise respect original edges. The model says nothing about two novel transitions in a 10+ word phrase, three or more new pairs, new vocabulary, different motif selection, or exact quotations outside the supplied archive. It reveals **zero** authenticated words from Emily's final inscription.

Together with [Emily's unrestricted four-word class](h17-k08-emily-fourword-unrestricted-vocabulary-20261106.md), [five-word class](h17-k08-emily-fiveword-unrestricted-vocabulary-5904m-20261106.md), [Emily-only one-new-edge 6..14](h17-k08-emily-one-new-bigram-692m-20261106.md) and [all-crew one-new-edge 6..12](h17-k08-crosscrew-one-new-bigram-465m-20261106.md), this is an additional disjoint *editing-operation constraint* (candidate sets can overlap across families). Further volume escalation without authentic final-version/copy evidence has low causal value. Pivot to an original terminal caption or a true original selected K04 coupon/source-generation bridge.

Original six accepted REC8 slots remain K01/K02/K03/K05/K06/K07 PASS; K04 and K08 MISSING; combined INCOMPLETE.
