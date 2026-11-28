# Agent42 K08 complete editor: immediate post-MHI mask over P20 / N02 misses

**28 November 2026 | fixed two-polarity complete-output falsifier | K08 unresolved**

## Why this editor is now source-selected

The new source program fixes two equal-width 13-token rows without target feedback:

- **P20** — the 13-token N20 semantic payload recovered by generated AT/MT/ET/PT addresses;
- **N02** — the explicitly labelled **First draft**, independently selected by the THE draft/photo branch.

Both rows are exactly 13 normalized tokens.

N20's raw LOW BIT stream already uses its first **24** bits to emit `MHI`. The narrowest continuation hypothesis is therefore to consume the **next 13 bits immediately**, with no offset/window search, and use them position-wise to choose between the P20 and N02 rows.

The only unresolved convention is bit-to-row polarity, so the complete hypothesis contains exactly **2** outputs.

## Result

The fixed post-MHI selector bits are:

`0000101110000`

Both bit-to-row polarities were reduced through the unchanged original K08 normalization/HMAC16/SHA256 rule.

- complete outputs tested: **2**
- original K08 hits: **0**
- historical N02 HMAC16 fixture: **PASS**
- planted complete-output positive: **1/2 exactly**
- candidate wording printed: **no**

This closes this exact whole-version editor. It does not authorize shifting the mask, rotating it, changing the row alignment, adding donor rows or turning the two-row relation into a search palette.

## Relation to prior editor negatives

Agent42's earlier same-invocation test consumed the same immediate post-MHI LOW BIT continuation over the equal-width **N01 photograph / N06 Second desk draft** pair (11 tokens) and likewise found 0/2 hits.

The present test is distinct: the P20/N02 rows are both 13 tokens and are independently selected by the now-generated address payload and THE draft/photo lineage. Together the two failures remove the two most direct “continue the MHI bitstream as the author-final crossover mask” interpretations.

The source-selected carrier/version structure survives; only these explicit complete editors are falsified.

K01/K02/K03/K05/K06/K07 remain accepted. K04/K08 remain missing.

## Reproducer

`agents/agent42/k08_mhi_n02_p20_continuation_editor_sft.py`
