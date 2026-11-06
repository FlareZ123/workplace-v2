# K04: one-based cassette-ticket byte locations with two prior-cache donors

**Agent 8, 6 November 2026. Complete original-source local test: 671,088,640 full K04 component SHA256 comparisons, zero original matches; planted full-coupon positive exactly once.** Source/route/acceptance/official verifier were not modified. K04 physical print and K08 authentic final caption remain missing; six established slots individually pass.

## New selected-coupon mechanism

The original 4 October service return register maps the selected north ESC-N job0417 to five L-29/N tickets ST-094, ST-081, ST-106, ST-099, ST-112. Agent45 already exhausted **all 2^40 five-byte repairs at the tickets modulo16 interpreted as zero-based byte offsets** `[14,1,10,3,0]`, with a successful complete audit. This is not a repeat of that exhausted support.

Here, the same five source ticket numbers are instead interpreted as **one-based ordinal byte positions**, namely `[(094-1)%16,(081-1)%16,(106-1)%16,(099-1)%16,(112-1)%16] = [13,0,9,2,15]`. Sorted as the source-program support: **[0,2,9,13,15]**. This alternative convention changes **three** byte positions relative to the previously exhausted zero-based support. The relationship from service-ticket numbers to coupon byte positions is a speculative reconstruction hypothesis, and the reconciliation is dated **after** the 3 October print. It does not authenticate any fault location.

To make a bounded physically interpretable source-cache model, suppose exactly two of these five physical bytes were stale bytes from one of two *earlier same-job* original spool objects: the 16:45 LABEL ACK attempt1 `E1E60D5F6B6DD2225FA6D5A2A63AD932` or the 18:01 RECOVER REQUESTED attempt1 `CD3E4F216ADB2FB180DA2AA90B33F7A4`. Keep the same byte index on each donor; allow donor choice independently at the two positions. The other three affected bytes are unrestricted 8bit values. The remaining eleven bytes equal the disputed reconstructed 18:02 ACK2 `A9A9DC5731A5E2AE879C47215C2559D5`.

This is a **post-event physical/copy defect** candidate family; the source does not establish it was the actual defect. The 18:03 request3 is deliberately excluded as future of the selected 18:02 ACK2 and cannot supply a causal stale cache.

## Full finite candidate reduction

Choose exactly two of five affected positions: `C(5,2)=10` choices. Each position gets one of two earlier same-job donor bytes: `2^2=4` choices. Enumerate all `2^24` possible other three bytes, giving **10 × 4 × 2^24 = 671,088,640 complete candidate assignments**. A candidate printed coupon is XORed with original route mask `8556C8CB6140A7F9A5123AC7571BEE1C`; all 32 bytes of `SHA256(component)` are checked against original immutable K04 target `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`.

This is an assignment count; families with three fully free bytes may contain overlapping complete coupon values. The whole 16byte SHA256 calculation is exact for each assignment, not a partial-bit or prefix-hash acceptance rule. The algorithm uses OpenSSL `SHA256_Transform` on the canonical 16-byte message padded to one 512-bit block; an independent ordinary `SHA256` planted whole-message digest agrees across all eight state words.

The original spool, fleet return docket, route, acceptance and exact selected row are pinned by source SHA/literals. Full original local execution from the supplied unchanged 46-member ZIP extraction returned:

```text
SUMMARY case=one-based-five-ticket-two-previous-cache-three-free smoke=0 tested=671088640 source_original_hits=0 planted_whole_hits=1
```

Prior 10,485,760-candidate smoke: `source_original_hits=0`, no planted witness as its chosen 24-bit value was intentionally outside smoke range. Planted coupon was constructed with two genuinely selected causal donor bytes and three specified other bytes, hashed with standard SHA256 and recovered **exactly once** in the complete original candidate enumeration. This verifies coverage of a nontrivial complete-coupon instance while preserving separation from the unchanged original acceptance target.

Exact locally executed C source SHA256: `c97e93a551d7b1365a845aa541faf2d584065da0a5f267e21b85a15cb5f86140`. The [source-pinned OpenMP C11 SFT](../agents/agent8/k04_ticket_onebased_two_cache_sft.c) is **Git blob `0cd8f1fa76b359f8c0050e422c0b7deb9e5b6c05`**, confirmed byte-identical to the executed original local source. It takes a directory containing the original `evidence/` and `acceptance.json`, optional `--smoke`; requires C11/OpenSSL libcrypto and OpenMP. It changes no source file.

## Limit and priority

The original K04 target is absent from this exact, source-derived **one-based five-position with two prior-cache-donor** family. This is a conditional exclusion, not evidence the true original coupon has any particular correct bytes or that the next-day five ticket IDs determined physical error locations. The rest of the one-based five-position `2^40` space was **not** exhausted here, and should be tackled only with additional selecting evidence or a justified budget. Agent45's zero-based `2^40` result remains disjoint in its explicit support. A verified pre-fire original physical witness or a successful genuine same-role source-to-physical reconstruction is still the best way to determine K04.

Original six accepted slots K01/K02/K03/K05/K06/K07 PASS; K04/K08 missing and combined REC8/1 INCOMPLETE. No original physical coupon bit became authenticated.
