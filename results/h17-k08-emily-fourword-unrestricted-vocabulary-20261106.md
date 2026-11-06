# K08: complete four-word product of Emily's original note vocabulary

**Agent 2 | 6 November 2026 | Original K08 NO_MATCH in 65,610,000 distinct complete candidates.**

## New reconstruction mechanism

The earlier [short normalized source-capsule search](h17-k08-short-normalized-source-capsules-20261106.md) checked arbitrary original-evidence **one/two-word** captions and arbitrary crew-source **three-word** captions. Existing source-bigram and two-strand studies constrained longer candidates to observed transitions or particular editorial constructions. This experiment asks a different, finite question: *could Emily's final inscription be any **four-word** title formed entirely from words she herself used, including novel transitions?*

The complete word inventory comes from original Emily note bodies N02, N06, N10, N13, N17, N18, N20 and N23. Extract ASCII `[A-Za-z0-9]+`, lowercase, deduplicate and sort. This gives exactly **90 words** (SHA256 of the newline-joined sorted vocabulary: `a323bd487dce87a6023e813c2e9756e9103df4f2f771f3e5c0455e0f1e11e261`). Bodies are included verbatim, so explanatory sentences and superseded-label vocabulary are intentionally included. The note file's original SHA256 is `13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb`.

Enumerate the ordered Cartesian fourth power `V × V × V × V`, permitting repeats, and join the four tokens with single spaces. The exact `90^4 = 65,610,000` strings are pairwise distinct. Test each through the untouched original K08 rule: `SHA256(HMAC_SHA256(bytes.fromhex(desk_nonce), normalized_phrase.encode())[:16])`, comparing all 32 digest bytes to `285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747`. The original nonce is `5F933DA6A1BD03C32DA5CBC25344F497`.

## Actual original-source execution

The optimized C++17/OpenSSL local executor `h17_author4.cpp` uses pre-initialized HMAC inner and outer SHA states. It verified all eight original note IDs, source SHA, 90 source word types, authentic original N02 first-draft HMAC16 `BF889359B0303F2B2B2FD96AE841210B`, and per-shard complete synthetic four-word positives.

| Original source-word first-index shard | Distinct complete captions | K08 original hits | Planted full positives |
| --- | ---: | ---: | ---: |
| 0..4 | 3,645,000 | 0 | 1 |
| 5..89 | 61,965,000 | 0 | 1 |
| **Total** | **65,610,000** | **0** | **2** |

Exact local executor output:

```text
source_sha256=13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb author_notes=8 words=90 range=0..5 complete=3645000 original_hits=0 planted_hits=1
source_sha256=13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb author_notes=8 words=90 range=5..90 complete=61965000 original_hits=0 planted_hits=1
```

The source extraction and reducer can be reproduced using `agents/agent2/k08_emily_fourword_product_sft.py` (portable standard-library reference implementation). The optimized original execution is specifically the C++17/OpenSSL local counterpart with the same enumerator and commitments.

## Limits and next attack

This is a rigorous finite negative for **four words each drawn from Emily's 90-note vocabulary**. It does not exclude new vocabulary, five-plus words, different encoded carriers, or a final author's distinct wording. It recovers zero terminal words. Do **not** enlarge this to a blind 90^5 search without a causal version or length witness; prioritise selected-vs-draft version evidence or a different source-derived mechanism.

**Recovery remains six of eight; K04 and K08 missing; combined INCOMPLETE.**
