# H-17 K08: N11 mug-shelf caption with N20's ordered sea/night/table motifs

**23 November 2026, Agent 7. Result: zero original K08 commitment matches.**

## Source-linked complete-phrase question

The source-local CREW4/LOW/ATEALBIT chain selects N11, David's **Mug shelf** body, as the note adjoining Emily's N10 "after the last cup" instruction. MAIL-12 independently describes a small card by the mug shelf, but does not quote it or say Emily adopted it. N20 explicitly lists Emily's desired scene elements in order: **sea**, **end of the night**, and **voices at the table**.

Could Emily's final wording be an order-preserving abridgment of the N11 mug-shelf sentence, with those three literal scene elements inserted in her stated order? This is a complete-output editorial hypothesis. The supposed copying relationship remains conditional; neither the source nor the existing source-selector controls establishes that she used N11 as a text base.

## Complete finite mechanism

- Source sentence N11 after its heading: "Even the chipped blue one belongs to someone who expects to see it again." This has 14 normalized words.
- Take every one of its 2^14 order-preserving word subsets, including empty and full.
- Insert **exactly** these three source-derived spans in this fixed semantic order: "the sea"; "at the end of the night"; "the voices at the table". Put them at any nondecreasing gaps between the retained N11 words. No invented synonym, extra token, or rearrangement.
- For a retained subset length k, there are (k+1)(k+2)(k+3)/6 gap triples. The complete assignment count is sum[k=0..14] C(14,k)*C(k+3,3) = **2,224,128**.
- For every complete normalized phrase, compute original HMAC-SHA256 with desk_nonce=5F933DA6A1BD03C32DA5CBC25344F497, take the first 16 bytes, then SHA256 that component and compare the complete digest to original K08 commitment 285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747.

The reproducible [single-file source-pinned test](../agents/agent7/k08_n11_mugshelf_three_scene_sft.py) checks original source SHA256s before candidate generation, verifies the original N02 HMAC known answer BF889359B0303F2B2B2FD96AE841210B, and recovers an in-family planted complete-caption target exactly once. It does not update source, acceptance, route, verifier, or candidate.

| Check | Outcome |
| --- | --- |
| Source fingerprints | exact |
| Original K08 complete HMAC/commitment evaluations | **2,224,128 assignments** |
| Original K08 matches | **0** |
| Planted in-family full-text control | **1 exact match** |
| Accepted archive component K08 | **MISSING** |

Executed locally against the unchanged original 46-file export and acceptance JSON on 23 November. The combinatorial total was independently checked by the closed-form sum above.

## Prior-art distinction and limit

This test is distinct from the 23 November **N09** 57,688,064-assignment full-caption edit study: it uses **N11**, the independently selected Mug shelf base text, with all ordered deletions and exactly three N20 motifs. Agent3's earlier bare N11 subsequences contained **no inserted motifs**; Agent2's earlier three-genre collage selected 2–8-token contiguous fragments from one photograph, one galley and one Emily note rather than arbitrary N11 deletions plus these fixed spans. The new negative therefore closes one clearly bounded N11-specific family without re-running those studies.

The failure supplies **no real K08 component**, no word of Emily's missing margin, and no historical source authentication of the N11-copy hypothesis. This editorial family should **not** be expanded into extra cues/synonyms simply because it failed. Seek a materially different version/copy mechanism or original author-final wording rather than larger unmotivated lexical grids. K01,K02,K03,K05,K06,K07 remain PASS; K04 and K08 remain MISSING; REC8/1 remains INCOMPLETE.
