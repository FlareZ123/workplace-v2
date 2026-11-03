# K08: genre-matched exact-label controls defeat literal-only reconstruction

**Agent 14 | 3 November 2026.** A source-only, target-free test on the two *known* Emily envelope labels identifies a specific failure of source-literal caption grammars. It neither recovers the missing keeper caption nor submits a K08 guess.

## Historical controls and correct masking

Original `evidence/crew/noticeboard-and-desk-notes.txt` (SHA-256 `13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb`) explicitly marks N17 as the standby-envelope label and N18 as the commissioning-envelope label. These are the two surviving *same inscription genre* texts; both are excluded as K08 by Emily's MAIL-11. The same MAIL-11 **quotes their wording**. A purported masked holdout that erases only N17/N18 from the crew extract leaks the answers through that email.

The self-contained [SFT](../agents/agent14/k08_envelope_label_holdout_sft.py) reads the original crew notes and all twenty original mails. It removes **both occurrences of each complete label** (one crew note, one MAIL-11 quotation; punctuation-optional, case-insensitive), normalizes ASCII word tokens, and assesses unigram and contiguous n-gram occurrence **within individual surviving source documents**, without manufacturing bigrams across file boundaries. Original genuine source 4- and 5-word spans pass positive controls.

| Known exact inscription | Source coverage after quote masking |
| --- | --- |
| N17 standby: `leave the light on for the next watch` | 7/8 word positions, 3/7 bigram positions, 1/6 trigram positions, **0/5 fourgram positions**. The exact singular word `light` occurs nowhere in the remaining crew + mail text. |
| N18 commissioning: `back before the first boat` | All five word positions occur somewhere, **0/4 bigrams**, no longer contiguous spans. |

The remaining MAIL-12 has `lights` (plural) and N06 has `lamp`. Thus regular singularization or semantic substitution can supply N17's missing exact token. N18 requires *fresh local word adjacency* even though its five word types all occur elsewhere. These are source facts, not evidence that Emily used a particular rewrite process.

## New cracking implication and boundaries

A K08 candidate mechanism that copies only intact source word spans of length ≥2 cannot generate the known commissioning-envelope control from this corpus, regardless of how many such spans it concatenates **unless it allows the needed single-word boundaries**. A generator constrained to the remaining exact unigram vocabulary cannot generate the standby label. This exposes an *architecture mismatch* for prior N13/N20/photograph 2–8-word-span copy/mosaic families: they lack structural coverage of both intact, same-genre historical labels, even before K08 is tested.

**Promising distinct next operation:** Build a purpose-conditioned inscription editor using word-level recomposition plus transparent, narrowly defined morphology/synonym operations, then score *both* leak-masked real-label controls before using it on N23's terminal keeper envelope. Maintain an explicit distinction between control reconstruction and historically authenticated author-final wording. Do not rerun broad literal-span permutations as a supposed independent attack.

This is a restricted two-control observation, not proof that the unknown K08 is outside any previous search class. The known texts are visible to investigators, so any later purported source-masked predictions are retrospective tests, not honest blindness. The original K08 HMAC, K04 SHA256, candidate and acceptance values were **never queried or changed in this experiment**. Recovery remains six PASS, K04/K08 missing, combined INCOMPLETE.
