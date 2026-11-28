# Agent42 K08 complete editor: N23 “heads twice” -> N01, COAT -> N07 reversal misses

**28 November 2026 | source-selected complete reversal operation | K08 unresolved**

## Fixed source program

The new N23 structural branch fixes all operands before reading K08 acceptance:

1. N23's final-text/carrier landmarks `wording / margin / envelope / words / it` have adjacent BETWEEN counts **2/6/3/4**, selecting N02/N06/N03/N04.
2. N04 literally says **“Count the heads twice”**.
3. HEAD low-bit packing across the four selected role-heading heads `First / Second / Kitchen / Under` selects **N14 Sunrise photograph**.
4. Apply HEAD a second time to N14's heading and it selects **N01**, the empty-bench photograph.

N04's final three body words supply a tighter continuation rather than another invented operator:

`NEEDS / A / COAT`

Apply the already established LOW BIT / LOW IF EVEN rule:

- `NEEDS -> 22 -> 23 = N23`
- `A -> 1 = N01`
- `COAT -> 7 = N07`

So N04's own terminal clause selects **both complete source operands, N23 and N01, plus the reversal record N07**. N07's first three post-label words are the already calibrated source-local reversal instruction used independently by the AES->SEA and LWOL->LOWL branches.

Thus the source-selected instruction closes as:

**N23 landmarks -> HEAD twice -> N01; NEEDS/A/COAT -> N23/N01/N07 reversal**

## Complete output test

Apply N07 reversal to the complete operands explicitly selected by the N04 terminal triple: **N23**, **N01**, and—because the selector order is NEEDS/A before the operator COAT—the single source-ordered combined object **N23 then N01**.

The short-token source calibrations establish reversal but not phrase granularity, so test exactly the two natural complete interpretations for each of those three fixed operands:

1. reverse complete **word order**;
2. reverse the entire normalized **character stream**.

There are no deletion, insertion, synonym, connector, source-row, operand-order or target-guided choices.

Original K08 result:

- complete outputs: **6**
- original K08 hits: **0**
- historical N02 reducer fixture: **PASS**
- planted full-output positive: **1/6 exactly**
- candidate wording printed/stored: **no**

Therefore the most literal complete continuation of N04's own “heads twice ... needs a coat” instruction is falsified for **both individual operands and their source-ordered combined object**.

## Scope

This negative does not weaken the N23 landmark-gap selector, the two HEAD passes, N01 as a selected antecedent, N23 as the final-margin witness, N07 as a calibrated reversal operation, or the source's draft/photo provenance. It closes only **whole-record reversal of the two explicitly selected N23/N01 operands and their source-ordered N23+N01 concatenation** under the NEEDS/A/COAT -> N23/N01/N07 continuation.

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
