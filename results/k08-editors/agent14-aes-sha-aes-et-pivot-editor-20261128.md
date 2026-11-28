# K08: AES/SHA/AES around the source-selected ET pivot — one-output MISS

**Agent 14 | 28 November 2026 | deterministic complete editor | no recovered K08 component**

## Question

The unique N09 operator stream is `AES / SHA / AES`. AES already has a target-blind source-local interpretation: LOW BIT(AES)=7 selects N07's calibrated reversal instruction, giving AES -> SEA. Can the middle SHA token select a pivot inside the newly fixed 13-token P20 payload strongly enough to turn the three-token stream into one complete authoring operation?

## Source-selected pivot

Apply the same established LOW BIT operation to `SHA`:

- LOW BIT(`SHA`) = **5**, selecting **N05**.
- The P20 carrier is already fixed independently inside N20.
- N05 and N20 have one unique maximal common normalized span of length two.
- That span is the existing **ET** segment in the AT/MT/ET/PT payload chain.
- Inside the 13-token P20 payload, ET partitions the payload into exactly **7 / 2 / 4** words.

Thus the source program itself supplies a natural three-part alignment:

`AES / SHA / AES`
→
`left-of-ET / ET-pivot / right-of-ET`

## Frozen editor

Use the independently calibrated AES operation as sequence reversal on the two flanking regions:

1. reverse the seven words left of ET;
2. preserve the two-word ET pivot;
3. reverse the four words right of ET.

This emits exactly **one complete 13-word normalized candidate**. No word choices, alternate pivots, rotations, insertions, deletions, lexical substitutions, modes, cryptographic keys, or target-selected completions are tested.

The complete candidate wording is not reproduced publicly; the source-pinned SFT reconstructs it.

## Source-vs-free decision ledger

| Decision | Source-fixed or free? |
| --- | --- |
| 13-token P20 carrier and PT stop | fixed by AT/MT/ET/PT cross-carrier chain |
| Middle SHA selector | fixed: LOW BIT(SHA)=5 -> N05 |
| Pivot | fixed: unique maximal N05/N20 common span, identical to existing ET |
| Left/right boundaries | fixed by P20 start/stop and ET pivot |
| AES operation | independently calibrated as reversal through N07 / AES->SEA |
| Apply the two AES tokens to the two flanking P20 word sequences | **single unverified authoring-edge hypothesis** |
| Per-word choices / alternative modes | none |
| Complete authored same-operation holdout | none survives |
| Reducer control | historical N02 HMAC16 fixture |

This is an authoring-operator falsifier, not an AES cipher search.

## Original result

Local execution against the unchanged source and original K08 acceptance:

```text
source_pin=PASS
p20_pin=PASS
sha_to_n05_et_pivot=PASS
aes_reversal_selector=PASS
partition=7/2/4
complete_candidates=1
historical_n02_control=PASS
original_k08_hits=0
```

**The single complete output misses K08.**

## Prior-art boundary

Repository search for the joint `AES SHA AES` / ET-pivot / P20 reversal construction found no earlier equivalent. Existing Agent45 work tested direct binary AES/SHA/AES block pipelines and separately established the target-blind AES/SEA reversal loop. Existing P20 work fixed the AT/MT/ET/PT payload but did not apply the N09 three-token program as a whole-text editor.

The same-day full-P20 reversal negative is different: it reverses all 13 words as one sequence. This test leaves the SHA-selected ET pivot fixed and reverses only the two source-defined flanks.

## Consequence

A direct text-level reading of the newly emitted three-token program is now closed: **reversal / ET pivot / reversal** does not produce Emily's accepted final wording.

This narrows the meaning of `AES/SHA/AES` without opening generic cryptography or prose grids. Any next interpretation should identify a different source-fixed operand/serialization or authoring relation before acceptance, rather than vary reversal granularity after this miss.

K01/K02/K03/K05/K06/K07 remain accepted. K04 and K08 remain missing; REC8/1 remains incomplete.

## Reproducer

`agents/agent14/k08_aes_sha_aes_et_pivot_sft.py`

The script pins the crew source and P20 payload fingerprint, recomputes LOW BIT(SHA), proves the unique N05/N20 ET pivot, applies the one predeclared flanking reversal, checks the historical N02 reducer fixture, and reports only aggregate control/outcome data.
