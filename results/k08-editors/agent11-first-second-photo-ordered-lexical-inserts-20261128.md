# K08: fixed First→Second→photo lexical insertions into source-ordered P20

**Agent 11 | 28 November 2026 | 942,824 distinct complete original-target captions | no original K08 match**

## New bounded authoring hypothesis

The independently composed source program reaches a sequence of records with explicit editorial roles: **N02 First draft → N06 Second desk draft → N01 photograph**. N20 separately supplies a fixed thirteen-token semantic payload P20, selected by the AT/MT/ET/PT cross-carrier path and SHA256-pinned at `4b3350e5b34e40cc9dd1ba53d926ef0455888aa056aac4ba7da141569664e95c`. Previously exhaustive P20-only deletion/reordering (152,152,845 distinct texts) and P20+exactly one ROOM (1,953,290,213) have no original commitment hit.

Could the final author compress the **P20 motif in its original order**, while inserting a few salient *exact original source words* in first-/second-draft/photograph role order? Freeze precisely one source-word identity per role:

- N02 First draft: **ROOM**, explicitly attested and echoed by MAIL-11's independent “making room” final-intent description.
- N06 Second draft: **LAMP**, concrete visual object also present in Emily's N13 end-of-night account.
- N01 selected photograph: **TEA**, singular distinctive closing object and N10's after-last-cup semantic reference.

The **word choices are heuristic**, not a source-defined extraction rule: each note contains other words. Their **order** is the already source-selected document-role lineage, rather than target-fitted. There is no evidence Emily literally concatenated these nouns. This is an exploratory **multi-source lexical addition and order-preserving P20 deletion** test, not a claimed authentic caption producer.

## Finite complete-output domain

For each of the 2^13 masks of P20's original 13 positions, preserve selected words in their original N20 order and insert selected new words in their fixed order into all weakly ordered gaps, including before the first and after the last retained P20 token. No other lexical changes, synonyms, word-order rearrangements or length bounds. Two frozen submodels:

1. N02+N06: exactly **ROOM→LAMP**, with each appearing exactly once, all P20 subsequences.
2. N02+N06+N01: exactly **ROOM→LAMP→TEA** once each, all P20 subsequences.

Because P20 contains repeated `the`, distinct mask assignments can yield identical complete normalized texts. The original target comparison deduplicates all complete captions by normalized text, so both complete **assignment counts** and **distinct candidate counts** are reported.

| Frozen added-word roles | Mask/gap assignments | Unique complete captions | Original K08 hits | Synthetic full-caption hits |
| --- | ---: | ---: | ---: | ---: |
| N02 → N06 | 274,432 | 208,688 | **0** | 1 |
| N02 → N06 → N01 | 940,032 | 734,136 | **0** | 1 |
| **Total** | **1,214,464** | **942,824** | **0** | 2 |

The two unique sets cannot overlap because the third has one TEA and the first lacks it. The assignments are algebraically `sum_{k=0..13} C(13,k)*C(k+m,m)` for `m=2,3`; original repeated-word duplicates are deducted in the counted distinct-caption column. All 2^13 P20 deletion masks and every fixed-order insertion position were executed locally on the original source extraction; ~4.78 seconds Python. No positive original K08 match.

## Controls and decision

The reproducer independently asserts the original crew note SHA256 `13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb`, exact original P20 digest, presence of all three role-specific source tokens, absence of those extra tokens from P20, original N02 historical HMAC16 fixture and **exactly one planted positive for each complete-output domain**. The original routing desk nonce/acceptance digest are read only from the untouched supplied archive. The original PDF, canonical candidate, source files and verifier are never altered, scanned or printed. Candidate wording and cryptographic components are not emitted.

**Conditional conclusion:** the K08 final wording cannot be obtained by an *order-preserving deletion of the fixed P20 semantic sequence plus only the two or three ordered source-role words above*, with no further lexical operations. This does **not** exclude a different noun, reversed role chronology, changing original word order, a novel authored word, or an entirely separate final inscription. Neither the role chain nor this no-hit provides the missing final words.

This is not a reason to start free lexical lattices with more objects. A valuable next direction is a **source-selected complete terminal operator** that fixes both the exact words and their ordering/stop choices, or a K04 original selected producer with independent intact whole-packet controls.

## Reproducer

`agents/agent11/k08_p20_first_second_photo_ordered_insert_sft.py`, run with `python agents/agent11/k08_p20_first_second_photo_ordered_insert_sft.py <original-extracted-root>`. Standard Python only, local source/nonce/acceptance, aggregate-only output.

**REC8/1 unchanged:** K01/K02/K03/K05/K06/K07 PASS; K04 and K08 MISSING; combined INCOMPLETE.
