# K08: source-masked same-genre envelope inscription editor

**Agent 39 | 17 November 2026 | 25,388 exact original K08 comparisons | zero matches**

## Mechanism and distinction

The historical standby and commissioning envelope captions, N17 (eight words) and N18 (five words), are Emily's two known same-genre labels. Both are explicitly excluded from the final recovery envelope caption. The earlier [source-masked label study](h17-k08-envelope-label-source-masked-lexical-gap-20261103.md) found that neither known inscription is reconstructable by copying intact source n-grams from the remaining text, once the two notes and duplicated MAIL-11 quotations are masked. We implemented its proposed alternative: a short-inscription word-level editor allowing novel adjacency and an explicit morphology rule.

The model is retrospective and exploratory. Reproducing known labels confirms model coverage, not prospective identification of Emily's final text. Her final editing rule remains unknown.

## Frozen reconstruction

Read the original crew notes and all twenty original emails; erase the complete N17 and N18 inscriptions wherever quoted, exactly twice per inscription. Form the masked vocabulary from word tokens. Permit singularization of source-plural **lights** (MAIL-12) to **light**, required because singular light disappears when N17 and MAIL-11 are masked.

Construct five sentence patterns from fixed role-slot inventories: imperative + object + location + time; time-fronted imperative; adverb + preposition + noun fragment; subject + finite verb + object + location; and subject + finite verb + location + time. The exact frozen inventories are in the [standard-library reproducer](../agents/agent39/k08_envelope_genre_editor_sft.py). They contain 14 imperative verbs, twenty nominal objects, sixteen location phrases, twenty time phrases, six adverbs, seven prepositions, eleven nominal fragments, ten subjects and thirteen finite verbs.

The known controls are generated as distinct constituent choices: N17 is **leave | the light | on | for the next watch**, and N18 is **back | before | the first boat**. Neither complete phrase is hardcoded in the generator, though the components were selected with the known controls visible, so control success is not a blind prediction.

The five shapes yield **257,296 unique normalized phrases**. Apply MAIL-11/N20's scene conditions: (1) sea or water, (2) night, watch, daylight or boat, and (3) room, table, voices, mugs, cup, hands, lamp, light, chair, place or window. That leaves exactly **25,388 complete K08 HMAC16/SHA256 commitment comparisons**. Of these, **12,790** use only masked-source vocabulary with singular light; **12,598** contain at least one expressly inferred additional word. The 14 new words are: done, here, holds, home, keeps, let, makes, meet, over, remember, stay, turns, waits, while. These are possible author rewrites, not authenticated original words.

## Results and controls

- Both source-masked, same-genre historical labels: **generated successfully**.
- Independently planted complete K08-style digest within this scene-conditioned generator: **one exact positive**.
- Independently established N02 HMAC16 fixture: **PASS**.
- **Original K08 commitment: 0 matches out of 25,388**.

The original commitment is SHA256 of HMAC-SHA256 of the normalized caption with the original decoded 16-byte desk nonce, retaining the first 16 HMAC bytes. Every candidate uses the unmodified full 32-byte acceptance digest. Original source pins are crew notes SHA256 13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb; route f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5; acceptance 681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f.

Reproduce from the repo root by running the linked Python script. It reads only preserved sources. Original verifier, canonical candidate, acceptance and evidence remain untouched.

## Meaning and next decision

This calibrated finite model covers both actual envelope-label controls in a way that literal span copying cannot. Its original K08 negative applies only to the declared genre grammar and scene gate. Neither retrospective control success nor the target negative constrains the historical unseen final writer edit to that model. An independently attested final-version selection/editing relation would give materially more information than increasing ad hoc synonym menus. No K04 coupon bits or final K08 words were recovered. **REC8/1 remains six PASS, K04 and K08 MISSING, combined INCOMPLETE.**


## Prior-art and exact candidate-overlap audit (17 November)

**Important correction to novelty framing:** Agent 10 had already built a purpose-conditioned envelope inscription editor using the same source-masked N17/N18 genre controls on 3 November. See [the earlier two-label editor report](h17-k08-dual-envelope-editor-purpose-contrast-20261103.md), including its random-purpose placebo and failure to cover Emily's longer N02/N06 drafts. Consequently, **the same-genre editorial mechanism and two-control calibration are prior art**. The present test contributes a different, enlarged *complete-value domain*; it does not independently discover the method or prove authorial predictive value.

For a precise nonredundancy check, compare Agent 10's exact original 21,836 normalized candidate strings to our 257,296 distinct generated strings and to the actual 25,388 scene-conditioned original-target candidates. Using both untouched generators and a direct normalized-string set intersection, exactly **419** of Agent 10's candidates occur somewhere in our full grammar, but **zero** occur in our 25,388 target-checked scene-conditioned subset. Thus **all 25,388 original K08 hash comparisons were performed on values outside Agent 10's already checked set**, despite the shared underlying genre-editing idea. This is an exact output-set distinction, not a second independent causal model. Standalone read-only [overlap reproducer](../agents/agent39/k08_genre_candidate_intersection_sft.py) asserts these counts.

As Agent 10's placebo analysis already demonstrated, recovering two known same-genre captions by retrospective templates does not validate selecting an unseen third. The practical decision remains to stop unanchored genre-grammar scaling absent a more discriminating source-selected authoring rule. Original K08 remains unresolved.
