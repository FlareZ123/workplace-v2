# K08: six-word Emily-lexicon captions with all three source themes

**Agent 5 | 16 November 2026 | original source target: NO_MATCH.**

## Exact new complete-caption universe

Emily's authored note bodies N02/N06/N10/N13/N17/N18/N20/N23 contain **90 distinct ASCII lowercase tokens** (including their own draft headings), SHA256 of the newline-joined sorted list `a323bd487dce87a6023e813c2e9756e9103df4f2f771f3e5c0455e0f1e11e261`. Her N20 source asks the final line to hold the **sea**, the **end of the night**, and the **voices at the table**. Test every possible six-word string, with repetition and any order permitted, over that fixed 90-word author vocabulary and require each whole string to contain:

- the literal word `sea`;
- the literal word `night`;
- at least one of the three literal author terms `room`, `table`, or `voices`.

There are **241,258,500 distinct complete normalized captions**: `90^6 - 2*89^6 - 87^6 + 88^6 + 2*86^6 - 85^6`. This model deliberately permits arbitrary cross-source word adjacencies; it is outside the earlier 1–5-word fully unrestricted search and does not assume all six words share source-attested bigram edges. It is an exploratory test, **not** a historical assertion that Emily's final phrase was six words long or used those literal terms. It does not imply anything about longer wording.

## Actual source-based original target run

- Immutable original notes SHA256: `13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb`.
- Original route desk nonce (hex): `5F933DA6A1BD03C32DA5CBC25344F497`.
- Original K08 full 256-bit commitment: `285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747`.
- Complete candidate reducer: `SHA256(HMAC_SHA256(nonce_bytes, entire_normalized_ASCII_caption)[:16])`.
- Known authentic N02 first-draft HMAC16 control `BF889359B0303F2B2B2FD96AE841210B`: PASS.
- Independent in-family full-caption plant `sea night voices table room good`: **one** synthetic target hit in the genuine six-word enumeration.

Source-pinned optimized local C++17/OpenSSL implementation completed **23 disjoint half-open first-word shards**, covering every first-word index `[0,90)` exactly once, with no shard failure. Sum of printed, individually completed full-phrase counts: **241,258,500**, in exact agreement with inclusion-exclusion; **zero** authentic K08 commitment hits, **one** synthetic complete-positive hit in shard `[68,69)`. Full inputs/nonce/target/verifier were never modified.

The [portable self-contained Python reproducer](../agents/agent5/k08_sixword_three_theme_sft.py) implements the same pruned exhaustive lexicon and target reducer with disjoint first-word sharding; the original fast C++ local execution supplied the reported full counts. Its sample original-source shard `[0,1)` also executed successfully with **1,378,290** complete checks and no original hit. A complete Python rerun of every shard is **not** independently claimed.

## Decision

This is a legitimate **bounded short-caption exclusion** with fully enumerated original-target strings, not an authenticated original final word. It gives no new coupon bits or accepted K08 component. Avoid rerunning these same six-word author-vocabulary captions or projecting the negative onto seven-word, expanded-vocabulary or paraphrased expressions. K01/K02/K03/K05/K06/K07 remain accepted; K04/K08 unresolved; combined REC8/1 incomplete.
