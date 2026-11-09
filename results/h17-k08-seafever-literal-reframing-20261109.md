# K08: source-specific *Sea Fever* literal/reframed late-watch caption trial

**Agent 8 | 9 November 2026 | Original K08: NO_MATCH.**

## Targeted recovery hypothesis

Emily's preserved N20 description asks for sea, the end of a long watch, and voices at a table. A separate public poem, John Masefield's *Sea Fever* (source: https://poets.org/poem/sea-fever), has water, the ending of a sailor's watch ("long trick"), and a companion's spoken story ("merry yarn") in the same short piece. This is a tighter thematic source candidate than an arbitrary unbounded maritime dictionary. It could supply a literal quote or small late-watch editorial reformulation of Emily's final line.

**Critical limitation:** None of the original H-17 records names Masefield, identifies that poem, establishes Emily read it, or indicates final envelope wording was a quotation. The theme alone is a weak source-selection rule. The exact original final caption is not preserved.

## Frozen exact candidate mechanisms

The [standard-library read-only single-file SFT](../agents/agent8/k08_seafever_literal_sft.py) reconstructs the original K08 route and commitment and asserts original SHA256 pins for notes, routing and acceptance, plus the independent real Emily N02 HMAC16 reference.

It evaluates three nonadaptive complete normalized-phrase families:

1. **All contiguous word windows** of the 12-line original poem, covering complete and internal quotes under the official K08 ASCII normalization.
2. **All nonempty selections of complete lines** in original poem order, including possible omissions of whole lines.
3. **Frozen small three-segment editorial rephrasings:** 14 source/topic heads, 12 source/topic bodies, and 14 source/topic tails. These include explicitly attested surviving Emily text, water/night/voices cues, and the poem's distinct "long trick" and story motifs. This is a bounded test, not a claim that Emily's final text used that structure.

For every unique normalized candidate, calculate `SHA256(HMAC-SHA256(K08 original desk nonce, phrase UTF8)[:16])` and compare all 256 bits with the **unchanged** original K08 commitment `285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747`.

## Executed original result

- **20,836 distinct normalized complete candidate phrases** tested.
- **0 accepted original K08 complete components**.
- Original exact N02 prehash HMAC16 fixture: PASS.
- Synthetic planted exact printed-line caption through the complete K08 reducer: PASS, detected once.
- No original evidence, acceptance, verifier, or canonical candidate mutation.

Execution was local against the original attached archive with source-byte hashes matching the repository. The committed SFT asserts the exact tested distinct-phrase count and contains the fixed source text and original commitment check. The author/title/copyright context is referenced at the Academy of American Poets page above.

## Decision

This closes the specific literal *Sea Fever* quote and small frozen source/scene reframing hypothesis. It supplies **zero independently attested final caption words** and does not change the six-PASS / K04-and-K08-MISSING / combined-INCOMPLETE state.

Do not widen this into arbitrary poetry, new rhyme vocabularies or large unsourced paraphrase grids. A future K08 attempt needs a newly identifiable literal final-version carrier or genuinely predictive authoring-stage operator. The poem is a failed conditional source hypothesis, not historical H-17 evidence.

## Independent repository execution

Manual GitHub Actions source replay [run 42589351287](https://github.com/FlareZ123/workplace-v2/actions/runs/42589351287) completed **SUCCESS** on 9 November 2026 at 08:54:47 UTC with both complete original evidence tests and synthetic controls. This confirms the checked-in portable Python SFT runs against the unmodified repository source. It does not improve historical source-model credibility or add an accepted recovery component.
