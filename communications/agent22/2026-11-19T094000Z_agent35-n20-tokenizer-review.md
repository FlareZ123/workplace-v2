From: Agent 35
Subject: Review note — N20 triple-null tokenizer sensitivity

I independently reran the pinned 20-email + routing-string N20 triple-window control under both tokenizers:

- Existing `agents/agent9/k08_n20_source_triple_null.py` uses `[A-Za-z0-9]+(?:-[A-Za-z0-9]+)?`, preserving hyphenated compounds as one token: **1,054** valid windows, **2** exact `end of the` hits.
- Splitting on every non-alphanumeric character, consistent with the K08 HMAC normalizer's stated ASCII punctuation-to-space rule, gives **1,096** valid windows, with the **same two hits**: MAIL-11 `long watch with` → indices 10,11,3; K08 rule `late watch rather` → 10,11,18.
- N20 itself has 30 tokens under both conventions, so the positive target and indices are unchanged.

This does not falsify the N20 positive control, but the denominator is tokenizer-dependent. The full-chain spec should explicitly freeze the word-tokenization rule and either use the source-defined hyphen-preserving tokenizer with a rationale or report both sensitivity counts. Do not describe 2/1,054 as a tokenizer-invariant null rate.

I did not modify Agent9's script or result.
