# H-17 K04: compose ACK2 leading-byte loss with four-word transport reordering

**Agent 25 | 3 November 2026.** A source-bound, explicitly *hypothetical* copy/serialization fault tested against the untouched original K04 commitment. **50,331,648 complete candidate assignments across two reducer-stage readings, zero accepted.** The six previously recovered components remain accepted; K04/K08 and the combined key remain unresolved.

## Distinct attack rather than another independent repair or reordering screen

The preserved ESC-N, PS-261003-0417, RECOVER, attempt-2 ACK copied buffer is **A9A9DC5731A5E2AE879C47215C2559D5**. Its unusual duplicated A9A9 leading bytes suggest *one possible* two-byte replacement sentinel, while original MAIL-16 explicitly warns the retained-fragment export lacks payload integrity and crew note N22 likens printer behavior to a fax. These are cues for a fault model, **not evidence that this specific fault occurred**.

Prior work had searched arbitrary leading or noncontiguous byte repairs on the retained ordering, word/fragment reordering without damage, bit-raster transposition without byte repairs, and different all-source quartet mosaics. This experiment tests their **composition**: two unknown original bytes **at the positions occupied by A9A9 in the copied buffer**, followed by a four-fragment transport serializer that can reorder four 32-bit groups and independently reverse bytes within each group. A changed order and a two-byte error can defeat either component screen alone.

For each of 24 permutations of the four 4-byte groups, each of the 16 choices of word-local byte reversals, and every 65,536 replacement for the original copied bytes 0–1:

1. Replace those two bytes, then apply the chosen four-word reserialization.
2. Apply the exact original route's **8556C8CB6140A7F9A5123AC7571BEE1C** mask by XOR to the transformed 16-byte coupon; SHA256 the resulting complete 16-byte K04 candidate against the original **930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0** commitment.
3. Also check the direct, non-XORed transformed buffer, as a separate stage-reinterpretation hypothesis, against the **same** original unchanged commitment.

Thus 24 × 16 × 65,536 × 2 = **50,331,648 complete stage assignments**. This counts assignments; no claim of global distinctness across stage representations is required. The original ZIP SHA256 is **e778552c555fac652e24fd09e1c4f31bd066b4686e624b91f6e94e1d64342bf7**; the source spool SHA256 is **7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083**. No upstream 128-bit value is treated as an authenticated physical print.

## Reproducer and outcomes

[Single-file portable C++17 / OpenSSL SFT](../agents/agent25/k04_joint_wordorder_sentinel_repair_sft.cpp). The in-memory planted positive uses a deliberately nonidentity word order (2,0,3,1), reversal mask 0b0101, and source first two bytes 1234. Its transformed, route-XORed full candidate is committed to a synthetic SHA256 target and rediscovered **exactly once** across the entire original-family enumeration. The original commitment is checked independently, with no alteration to official sources or verifier.

Local full execution, compiled with optimized C++17 and linked against OpenSSL:

- 25,165,824 copied-coupon-then-mask complete candidates: **zero original K04 matches**.
- 25,165,824 direct component-stage complete candidates: **zero original K04 matches**.
- Planted complete synthetic matching transformation: **one of one**.
- Runtime on current local session: about **15.2 seconds**.

**Scope:** This excludes the selected buffer's *first two copied bytes* being arbitrary while its other 14 copied bytes survive under any of these 384 word-order/word-local reversal transformations, for both specified reducer interpretations. It does not exclude a different corruption location, 3+ corrupt bytes, more general raster/bit permutations composed with corruption, a bad mask, a different genuine coupon upstream, or an unrelated generator mechanism. No new verified K04 target bit follows, and K08 exact final wording remains unknown.

This scoped negative is useful because it prevents silently combining two previously failed one-step mechanisms into a purported new recovery claim without confronting the full original commitment. It should not be expanded into a huge unfocused corruption search absent stronger source evidence.
