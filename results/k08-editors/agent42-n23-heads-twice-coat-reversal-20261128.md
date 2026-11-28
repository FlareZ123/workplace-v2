# Agent42 K08 complete editor: N23 “heads twice” -> N01, COAT -> N07 reversal misses

**28 November 2026 | source-selected complete reversal operation | K08 unresolved**

## Fixed source program

The new N23 structural branch fixes all operands before reading K08 acceptance:

1. N23's final-text/carrier landmarks `wording / margin / envelope / words / it` have adjacent BETWEEN counts **2/6/3/4**, selecting N02/N06/N03/N04.
2. N04 literally says **“Count the heads twice”**.
3. HEAD low-bit packing across the four selected role-heading heads `First / Second / Kitchen / Under` selects **N14 Sunrise photograph**.
4. Apply HEAD a second time to N14's heading and it selects **N01**, the empty-bench photograph.

N04's final noun supplies a direct continuation rather than another invented operator:

`LOW BIT(COAT) = 7 -> N07`

N07's first three post-label words are the already calibrated source-local reversal instruction used independently by the AES->SEA and LWOL->LOWL branches.

Thus the complete source-selected instruction is:

**N23 landmarks -> HEAD twice -> N01 -> COAT/LOW BIT -> N07 reversal**

## Complete output test

Apply N07 reversal to the **entire** selected N01 caption.

The short-token source calibrations establish reversal but not phrase granularity, so test exactly the two natural complete interpretations:

1. reverse complete **word order**;
2. reverse the entire normalized **character stream**.

There are no deletion, insertion, synonym, connector, source-row or target-guided choices.

Original K08 result:

- complete outputs: **2**
- original K08 hits: **0**
- historical N02 reducer fixture: **PASS**
- planted full-output positive: **1/2 exactly**
- candidate wording printed/stored: **no**

Therefore the most literal complete continuation of N04's own “heads twice ... coat” instruction is falsified.

## Scope

This negative does not weaken the N23 landmark-gap selector, the two HEAD passes, N01 as a selected antecedent, N07 as a calibrated reversal operation, or the source's draft/photo provenance. It closes only **whole-caption reversal of N01** under the source-selected COAT->N07 continuation.

Do not extend this miss into arbitrary partial reversals, token-block permutations or hand-picked cut points. Those are different editor families and would require a new source-visible selection rule.

Together with Agent11's exhaustive P20-only wordbag closure and Agent42's 0/2 N01+P20 shared-AT whole-source merge, the terminal branch now has three direct complete-output failures:

- P20 alone under arbitrary source-vocabulary deletion/reordering: closed by Agent11;
- complete N01 + P20 shared-AT merge: closed;
- complete N01 under source-selected N07 reversal: closed.

A surviving terminal rule therefore needs a **specific source-fixed lexical substitution/addition or a genuinely different complete authoring operation**.

## Reproducer

`agents/agent42/k08_n23_heads_twice_coat_reversal_sft.py`

The script pins the original note source, reproduces N23 landmark counts, both HEAD passes, COAT->N07, both complete reversal granularities, historical reducer control and planted positive. It uses the original K08 commitment only for final complete-output verification.

K01/K02/K03/K05/K06/K07 remain accepted. K04/K08 remain missing.
