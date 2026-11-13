# K08 bounded candidate result: mug-as-person metonymy

**Status:** bounded negative; no K08 value recovered or promoted.

## Question

Can the final welcome phrase be constructed by treating a mug as a proxy for the returning crew member who owns it?

## Source basis

This is a specific object-to-person relation, not merely a generic table/water/night paraphrase:

- N11 says the chipped blue mug belongs to someone who expects to see it again.
- N19 explicitly contrasts counting mugs with counting beds: a bed does not tell whether anybody has sat down.
- MAIL-12 says the chipped blue mugs belong to two night crew members, who know which ones are theirs.
- N13 places mugs beside the window at the end of the night; N20 asks for sea, end-of-night and voices at the table.
- MAIL-11 says the envelope phrase is more like a welcome and describes people making room for each other after a long watch.

## Frozen operation

Convert the mug from an object into a token of a returning/expected crew member, then express that relation as a complete welcoming caption. The finite 20-phrase candidate set and source pins are preserved in `agents/agent4/k08_mug_metonymy_sft.py`.

The script verifies the exact source-file hashes, uses the unchanged K08 nonce and acceptance commitment, and checks the known N02 HMAC control before testing candidates.

## Result

- Complete candidates: **20**
- K08 commitment hits: **0**
- Route, nonce, acceptance, verifier and archive files changed: **none**

This closes only this frozen metonymy family. It does not show that Emily used this transformation, and it does not rule out a different source-grounded phrase. The model has no same-role final-caption holdout; that limitation is explicit. Agent3 has been asked to adversarially assess whether this family is materially distinct from the existing MAIL-11 caption grammars.

## Next action

Do not expand this into generic mug/cup/welcome synonyms. If Agent3 judges it already subsumed, close it. Otherwise preserve it as a bounded negative and continue only when a new authenticated source edge or materially distinct authoring operation is available.
