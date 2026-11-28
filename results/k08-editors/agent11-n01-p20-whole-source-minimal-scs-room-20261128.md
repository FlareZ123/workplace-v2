# K08: N01 + P20 entire-row minimum-SCS, optionally one source ROOM — 4,031,040 original misses

**Agent 11 | 28 November 2026 | complete source-selected two-strand terminal editor | no K08 recovery**

## Why this is an actual new, bounded editor test

The current target-blind source program selects two independent pieces with a literal two-word **THE SEA** overlap:

- **N01**: the entire 11-token original photograph-of-empty-bench caption selected by N23 landmarks -> N04 **HEAD twice** -> N14 -> N01 and corroborated by N10's reference to the photograph after the last cup;
- **P20**: the 13-token source-selected scene payload of Emily N20, fingerprint `4b3350e5b34e40cc9dd1ba53d926ef0455888aa056aac4ba7da141569664e95c`, selected by the AT/MT/ET/PT cross-carrier decoder.

Agent42's earlier [shared-prefix whole-row merge](agent42-n01-p20-shared-at-complete-editor-20261128.md) tried the two *concatenation* continuations beyond the common prefix, yielding 0/2 original matches. This test extends that narrowly to the mathematical **shortest common supersequence of both entire source rows**, retaining every source word and source-internal order, coalescing the common source-verified prefix once, and interleaving their two remaining suffixes while minimizing total length. This admits non-concatenated complete strings **not** covered by those two original assignments.

It differs from [Agent21's two-source word-interweave](../h17-k08-photo-desk-word-interweave-20261106.md), which only used **3–9-word fragments**, and from [Agent43's three-strand minimum SCS](../h17-k08-three-strand-scs-minimal-editor-20261115.md), which selected different shorter three-role fragments. This test uses **exactly the full newly source-selected 11+13-token pair**, without arbitrary span cuts or source-role selection.

A second finite option adds **exactly one `room`**, attested independently by selected Emily N02 First draft and MAIL-11's stated desire for **making room**. That is the *only* lexical addition; all 22 fixed-source words remain. The original one-ROOM wordbag result allows deleting source words and rearranging P20 alone, but lacks N01's distinct terms; this full-row test is not contained in it.

## Exact combinatorial domain

The fixed prefix is `the sea`; outside that prefix, **N01's nine residual token types are disjoint from P20's eleven residual token types**. Therefore the minimal full-word supersequence length is **22** and each complete string is determined uniquely by the choice of which 9 of the 20 suffix positions receive N01's ordered suffix tokens.

`C(20,9) = 167,960` distinct normalized **22-word** whole-source outputs.

The one-ROOM option places the new token at any of **23 gaps**, without changing order, yielding exactly `167,960 × 23 = 3,863,080` additional **23-word** complete outputs. Since ROOM is absent from N01 and P20, these are distinct both from one another and from the plain outputs.

**Total tested: 4,031,040 unique complete normalized captions**, with no arbitrary vocabulary, no missing source words, no synonym grid and no post-hoc length threshold.

The interleaving itself is **free**, not source-selected. Neither retained record says Emily authored a shortest supersequence, so this is a bounded editorial-model falsifier, not a historical authenticity claim.

## Original-target test and controls

Original source SHA256 `13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb` and P20 SHA are asserted. The original nonce is taken from recovery routing, the complete K08 acceptance target from unchanged acceptance, no PDF. Each candidate gets the original `SHA256(HMAC_SHA256(desk_nonce, normalized_sentence)[:16])` reducer, with an independent historical N02 first-draft HMAC16 fixture (`BF889359B0303F2B2B2FD96AE841210B`) and two separately planted, full-output synthetic positive checks.

Local source run:

```json
{
  "model": "full_N01_P20_minimal_two_strand_SCS_plus_optional_one_source_ROOM",
  "source_sha": "PASS",
  "P20_SHA": "PASS",
  "N02_HMAC16": "PASS",
  "plain_complete_unique": 167960,
  "plus_room_complete_unique": 3863080,
  "total_complete_unique": 4031040,
  "original_hits": 0,
  "planted_plain_hits": 1,
  "planted_room_hits": 1
}
```

Wall time ~11.3 seconds in original-source local Python, no original candidate text or component printed. The code pins N01/P20 lengths, shared prefix, disjoint source suffixes, ROOM source evidence, exact combinatorial denominators and positive controls.

## Consequence and decision

The source-selected **complete N01 photograph caption** and **complete P20 Emily scene span**, both preserving all their original words and order with only shared `the sea` coalescence, cannot produce the author-final K08 line by *any minimum-length word interleaving*, even if exactly one N02/MAIL-11-attested ROOM is inserted at an arbitrary position.

This does **not** rule out dropping parts of N01, adding multiple new words, grammatical rewriting, different source operands or alternate author-final versions. The actual 22/23-word final-caption lengths are not source-attested and may be less plausible than a shorter human-written inscription. The result closes an exact **entire-row source-selected pair**, not all plausible photo/desk phrase editing.

The next viable test needs a source-fixed **selection of which actual source words survive and what exactly gets written**, ideally calibrated on an independently retained whole authoring transition. Do not generalize this miss into authority to expand unconstrained lexical palettes.

## Reproducer

`agents/agent11/k08_n01_p20_fullscs_room_sft.py` — invoke with the original extracted archive root, e.g. `python agents/agent11/k08_n01_p20_fullscs_room_sft.py <extracted-archive-root>`. No external libraries or network use.

**Acceptance remains K01/K02/K03/K05/K06/K07 PASS, K04/K08 MISSING, REC8/1 INCOMPLETE.**
