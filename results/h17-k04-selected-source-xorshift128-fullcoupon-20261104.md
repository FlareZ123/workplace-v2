# K04: complete selected-source reversible xorshift128 sequence, negative

**Agent 10 | 4 November 2026 | source-pinned local execution | original K04 NO_MATCH.** Original REC8/1 remains K01, K02, K03, K05, K06, K07 individually PASS, with K04 and K08 MISSING and combined INCOMPLETE.

## What is new

The recently identified MAIL13/MAIL16 future-event descriptions challenge treating represented historical timestamps as source-production chronology. This experiment accordingly asks a different question from printer-only continuation or the K02-to-K05 97-word heldout: **could the five independently selected, full original 16-byte source objects be positions in a common reversible 128-bit output sequence, in an unknown production order?** A common generator would potentially reconstruct the whole selected K04 physical coupon even if its copied spool buffer is false. The proposed generator is Marsaglia xorshift128 with one 32-bit output per step; no original record attests it or its use for printer coupons.

Source objects, all independently validated through existing original selected-slot reconstructions: K01 \`049AAB2E1CDE7A82CD7C60234303C91A\`; K02 selected prehash \`E1A5E474BAD7E853A2E8C71D3317D507\`; K05 \`FF8B78200A56E8586DCDA00EF01E4572\`; K06 \`5DBF40EE52FAAED9A536D3326CF0D95A\`; K07 selected prehash \`8947CEDCB9CC73BAB7E87BE63302C5C9\`. This excludes the disputed K04 spool copy from model fitting.

## Computation

Every complete 16-byte source is interpreted as four consecutive xorshift128 32-bit outputs in four serializer views: forward/reversed word order and native/reversed bytes in each word. The state after four outputs is exactly the four observed outputs. Hence the generator can be stepped forward **or backward** without guessing an unknown starting 128-bit state. From each of five anchors and four input views, examine 200,000 exact forward and 200,000 exact backward successor states. Compare each with each of the other four independently selected source objects under all four views. In addition, emit all four complete 16-byte target serializer views at each step, XOR the unmodified K04 mask, and SHA256 the complete 16-byte component against the unmodified K04 commitment.

Five anchors × four input views × two directions × 200,000 steps × four output views = **32,000,000 full original K04 SHA256 comparisons**, zero matches. Across the same sequence walks, **zero entire selected source-block holdouts match** (comparisons are cheap full-128-bit equality and only require a known source).

Original-source SHA256 pins: notes/mail03 \`3cf886c12e094cb0362999c5a4d93f913c848a64471f833fbddbfdc2d57ff889\`; telemetry \`3787dbd6bab3930ea5293c25a995175161a1c0d7683daad29f498026e057639f\`; recorder \`5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba\`; procedures \`a4b649fdbb6909115fb9505133012b5c1dda42141aafc1c6ec756199ddf1fc6d\`; transfers \`32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf\`; route \`f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5\`; acceptance \`681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f\`.

## Positive controls and reproducibility

The [source-pinned single-file C++17/OpenSSL reproducer](../agents/agent10/k04_selected_source_xorshift128_sft.cpp) passed 1,000 exact forward/backward state round trips and all four binary serializers; a genuinely planted state, independent output view and offset137 produced an exact **full masked synthetic coupon SHA256** match while a separate synthetic heldout state at offset57 was found. Its compiled local run on the unmodified original 46-member ZIP extracted to disk returned:

\`\`\`
ORIGINAL_SOURCE_PINS_PASS files=7
SYNTHETIC_INVERSION_PASS 1000 state round trips all4 serializers
SYNTHETIC_COMPLETE_COUPON_PASS offset=137 positive_holdout=57
ORIGINAL_NO_MATCH complete_sha256_checks=32000000 original_source_holdouts=0 source_anchors=5 views=4 directions=2 offsets=1..200000
\`\`\`

Run with an extracted ZIP root or the repository's \`resources\` root as the sole argument. The search does not edit original evidence, acceptance, or candidate.

This is a new **full target-reaching selected-only cross-source** mechanism, with a separate original-to-original heldout. It is **not** an authentication of an actual historical xorshift emitter. A different generator, source-to-state transformation, sampling interval, selected ACK coupon or unquoted Emily final words remain outside the test. Authenticated original selected K04 coupon bits remain zero of 128; exact final K08 words remain zero.
