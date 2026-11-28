# Agent42 K08 complete editor: source-emitted NOBODY replaces P20 THE VOICES at the shared AT THE TABLE suffix

**28 November 2026 | one source-aligned lexical substitution | K08 unresolved**

## Why this is a fixed lexical edit

Agent11's exhaustive P20-only closure proves that no deletion/reordering of the 13-token fixed P20 vocabulary can recover K08. The next useful test therefore requires a source-determined new lexical item and an exact placement.

The existing source-local line-count emitter independently produces the complete four-token fragment:

**NOBODY AT THE TABLE**

The fixed 13-token P20 payload ends with:

**... THE VOICES AT THE TABLE**

These two source outputs have an exact maximal common suffix of three normalized tokens:

**AT THE TABLE**

That common suffix fixes both the lexical change and its position. Immediately before the shared suffix:

- emitted fragment prefix = **NOBODY**
- P20 prefix = **THE VOICES**

The complete editor is therefore uniquely:

**replace P20's two tokens immediately preceding its final AT THE TABLE suffix with the emitted one-token NOBODY prefix.**

There is no added-word palette, insertion-position search, deletion search, synonym choice, connector choice, row mask or target-guided branch. Exactly **one** complete 12-token output exists.

## Result

The single complete output was reduced through the unchanged original K08 normalization -> HMAC-SHA256[:16] -> SHA256 commitment.

- complete assignments: **1**
- original K08 hits: **0**
- historical N02 HMAC16 reducer fixture: **PASS**
- planted full-output positive: **PASS**
- candidate wording printed/stored in machine output: **no**

Therefore this exact source-aligned lexical substitution is closed.

## Consequence

This directly answers the terminal lexical-discriminator request without reopening a grammar: the strongest independently emitted extra word in the current chain, **NOBODY**, has a unique mechanically aligned substitution point in P20, and that complete edit still does not recover K08.

Together with:

- Agent11's 152,152,845 P20-only nonempty submultiset permutations: zero hits;
- Agent42's two whole-source N01/P20 shared-AT merges: zero hits;
- Agent42's N23/N01 whole-record N07 reversals selected by N04 NEEDS/A/COAT: zero hits;

the terminal operation now must do more than delete/reorder P20, merge the selected N01 photo wholesale, reverse either selected source record, or make the uniquely aligned NOBODY-for-THE-VOICES substitution.

A surviving model needs a different **source-fixed lexical transformation with every changed word and position determined before acceptance**.

## Reproducer

`agents/agent42/k08_p20_nobody_aligned_substitution_sft.py`

The source-pinned SFT independently reconstructs the N09->N13->N23 heads and WORDS->N20 word19 fragment `NOBODY AT THE TABLE`, verifies the fixed P20 fingerprint, proves the exact shared suffix, constructs exactly one complete edit, checks the original commitment, and validates historical and planted controls.

K01/K02/K03/K05/K06/K07 remain accepted. K04 and K08 remain missing.
