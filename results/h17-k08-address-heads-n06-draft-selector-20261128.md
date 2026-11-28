# K08: AT/MT/ET/PT address heads select Emily's N06 second desk draft

**Agent 14 | 28 November 2026 | target-blind source-program continuation | final wording still unresolved**

## Result

The completed K08 overlap decoder uses the fixed ordered addresses:

`AT -> MT -> ET -> PT`

Their changing first coordinate is **AMEP** and their invariant second coordinate is **TTTT**.

Using only operators already established elsewhere in the source program:

1. LOW BIT(`AMEP`) = **7**, selecting N07, the independently calibrated reversal instruction.
2. A1Z26 `AMEP` addresses N01/N13/N05/N16.
3. Those four post-label note bodies contain **11/22/14/11** normalized words.
4. Under the established A=0 count-to-letter convention, those counts emit **LWOL**.
5. Apply the selected N07 reversal: **LWOL -> LOWL**.
6. Apply the already-established whole-token LOW BIT reduction to `LOWL`: **6**.
7. N06 is Emily's source-labelled **Second desk draft**.

The invariant address column provides a matched null: LOW BIT(`TTTT`) = 0, outside the N01..N24 note namespace.

No K08 nonce, acceptance commitment or candidate wording is read.

## Why this supersedes the weaker LOW+L split

The same invocation initially noticed that `LOWL` can be visually segmented as the known operator `LOW` plus residual `L`, and that carrying L through LOW IF EVEN reaches N13 and then N23. That composition is recorded in [the N23 lineage note](h17-k08-address-heads-n23-version-lineage-20261128.md), but it requires an extra token-splitting grammar rule that the source never states.

The whole-token reduction above is cleaner because this exact style of operation already has a direct source-program precedent: the authoritative K08 source field reduces to **VLOWL**, and prior work applies LOW BIT to that entire emitted count token to obtain N12. Applying the same operation to the new whole token `LOWL` gives N06 with no split.

Therefore **LOWL -> LOW BIT -> N06 is the primary continuation**. The `LOW + L -> N13 -> N23` path is retained only as a secondary, explicitly less-supported interpretation.

## Source-vs-free ledger

| Step | Status |
| --- | --- |
| AT/MT/ET/PT order | fixed by independent payload decoder |
| Use changing coordinate AMEP | source-discriminated; invariant TTTT reduces to invalid selector 0 |
| AMEP LOW BIT -> N07 | fixed |
| AMEP A1Z26 note addresses | fixed |
| Note counts 11/22/14/11 | fixed source values |
| A=0 count-letter mapping | established source-program convention |
| N07 reversal LWOL -> LOWL | selected and independently calibrated |
| Whole-token LOW BIT(LOWL) -> 6 | established operator application, matching VLOWL precedent |
| N06 role | source-labelled second desk draft |
| Exact final edit from N06 to keeper envelope | **still missing** |

## Independent heading-channel corroboration

After N06 is selected by the address-head route, reuse the **already-established N09 heading channels** as a control rather than as a second selector. N06's three heading words produce HEAD / adjusted TAILBIT / adjusted LEN values **1 / 3 / 5**, i.e. A1Z26 token **ACE**. Among the 13 colon headings whose adjusted three-channel values all lie inside N01..N24, N06 is the **only** one with the exact ACE signature.

This signature feeds the same source-local machinery without consulting acceptance:

- A1Z26 `ACE` -> N01/N03/N05;
- their normalized post-label counts are **11/12/14** -> A=0 count token **LMO**;
- the already selected N07 reversal gives **OML**;
- whole-token LOW BIT(`OML`) = **3**, selecting N03, source-labelled **Kitchen photograph**.

The simpler observation LOW BIT(`ACE`)=7 is **not** selective: many eligible headings low-bit to 7, so it is not used as evidence. The useful corroboration is the unique full three-channel ACE signature followed by the fixed count/reversal/whole-token reduction chain to the photograph role. This does not prove a historical edit edge or emit final wording; it supplies internal redundancy for the independently selected N06 branch and aligns with MAIL-11's source-class statement that desk notes and photograph captions informed the keeper wording.

## Consequence

The completed AT/MT/ET/PT semantic-payload decoder now has a direct target-blind continuation to an actual **Emily-authored draft node**, rather than only to a thematic source or an inferred final-carrier class.

That materially sharpens the remaining K08 problem. The selected draft is N06, but N06 itself is not the accepted final wording: earlier complete/deletion-only checks already include its literal text and do not recover K08, and the version graph classifies it as a draft rather than the keeper-envelope final.

Do not expand N06 into another synonym or clause grammar. The next useful step is a source-fixed **N06 -> final-version** operation or a separately selected later carrier.

K01/K02/K03/K05/K06/K07 remain accepted. K04 and K08 remain missing; REC8/1 remains incomplete.

## Reproducer

`agents/agent14/k08_address_heads_to_n06_sft.py`

The script pins the crew-note source, reproduces the address columns, AMEP->N07 selector, count token, selected reversal and whole-token LOW BIT reduction, and checks N06's labelled draft role without reading K08 target data.
