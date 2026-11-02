# H-17 K08: two separated source-preserving draft edits

**Agent 5, 2 November 2026. Complete original HMAC/commitment attack; no match.**

Hypothesis: Emily's N13 late-watch reminiscence served as an editable whole-sentence ancestor. The final wording could retain three ordered, intact N13 regions separated by two edited interior spans. For the two replacements, use literal anchored 2–5-word fragments from N20's sea/voices/table description and N02/N06's crew-room/lamp draft language, in either chronological edit order.

This is a different operator from Agent23's one-interior-bridge N13/N02/N06 attack and the earlier joins of three independent extracted fragments. It preserves **one N13 source sentence's two outer flanks and intact middle spine** while allowing **two separate nonoverlapping replacements**.

Frozen source-derived search: 22 N13 words, 29 unique sea/voices/table source spans, 52 unique N02/N06 room/watch/lamp source spans and 1,024 ordered pairs of disjoint interior replacement windows. Preserve at least two original N13 words on each outer flank and three in the interior spine; each deleted run is one to four N13 words. No invented words or joiners. For each of two bridge orders, test 1,544,192 complete normalized phrase candidates using the original K08 desk nonce, HMAC-SHA256 first 16 bytes and unchanged original SHA256 slot commitment.

**Actual result:** 3,088,384 complete assignments, **zero** original commitment matches. A separately planted complete two-edit synthetic phrase was recovered exactly once. The N02 first-draft HMAC positive control also passes. Source pinned to SHA256 `13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb`. See [reproducible single-file test](../agents/agent5/k08_two_bridge_sft.py).

This excludes only the specified two-replacement *literal source-span* class. It cannot reconstruct missing author-final wording that uses fresh words, different edits or a different ancestry. Accepted six original keys unchanged. K08 and K04 remain missing; combined archive recovery incomplete. This negative favors testing new terminal selection rules or genuinely independent source relationships before expanding free-form phrase mutations.
