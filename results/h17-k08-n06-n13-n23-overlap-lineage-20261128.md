# K08: AT/MT/ET/PT now gives a source-fixed N06 -> N13 -> N23 version lineage

**Agent 14 | 28 November 2026 | target-blind source-program composition | final wording still unresolved**

## Result

The fixed K08 overlap decoder can now be continued from its completed N20 semantic payload to an Emily draft and then to the surviving final-margin witness **without the speculative LOW+L token split**.

The chain is:

`AT/MT/ET/PT -> AMEP -> N07 -> LWOL -> LOWL -> N06 -> N13 -> N23`

Every transition uses an operator already established elsewhere in the source program.

## Stage 1: address chain -> N06 second desk draft

The ordered overlap addresses are fixed independently as:

`AT -> MT -> ET -> PT`

Their changing first coordinate is **AMEP**; their invariant second coordinate is **TTTT**.

- LOW BIT(`AMEP`) = **7**, selecting N07, the independently calibrated reversal instruction.
- LOW BIT(`TTTT`) = **0**, outside the N01..N24 namespace.
- A1Z26 `AMEP` addresses N01/N13/N05/N16.
- Their normalized post-label word counts are **11/22/14/11**.
- Under the established A=0 count alphabet, that emits **LWOL**.
- N07 reversal gives **LOWL**.
- Apply the established whole-token LOW BIT reduction: LOW BIT(`LOWL`) = **6**.
- N06 is Emily's source-labelled **Second desk draft**.

This direct whole-token reduction is the primary address-head continuation. It supersedes the weaker same-invocation attempt to split `LOWL` into `LOW + L`.

## Stage 2: N06 -> N13 by the existing maximal-overlap rule

Reuse the same exact-contiguous-overlap relation already used by the AT/MT/ET/PT decoder.

Compare the selected N06 body against each of the other **23** numbered note bodies. N13 is the **unique** partner with the longest exact contiguous common span:

- selected-note partner denominator: **23**;
- unique winning partner: **N13**;
- common-span length: **3 normalized words**;
- span SHA-256: `2ab57327d0317a1f28546095fb2cccbafc190fd90d4bbff5f19a64637d6a3e8f`.

The public report deliberately records the fingerprint rather than reproducing the source phrase.

As a whole-corpus control across all **276 unordered note pairs**:

- exactly **one** pair has a maximal common span of length 5;
- no pair has maximal length 4;
- exactly **two** pairs have maximal length 3.

The selected-N06 rule does not choose between those two corpus-level length-3 pairs: starting from N06, N13 is its unique strongest partner.

## Stage 3: N13 -> N23

N13 contains **22** normalized post-label words. Apply the already-established **LOW IF EVEN** count transition:

`22 -> 23`

This selects N23, Emily's surviving record that identifies the final-margin/final-envelope wording but does not quote it.

No K08 nonce, commitment or candidate phrase is used anywhere in this lineage.

## Source-vs-free ledger

| Step | Status |
| --- | --- |
| AT/MT/ET/PT and order | fixed by independent cross-carrier payload decoder |
| AMEP vs TTTT coordinate | source-discriminated by valid-note LOW BIT result 7 vs invalid 0 |
| AMEP -> N07 | fixed LOW BIT |
| AMEP -> note counts -> LWOL | fixed A1Z26/count mapping |
| N07 reversal -> LOWL | independently calibrated operation |
| LOW BIT(LOWL) -> N06 | established whole-token reduction, matching prior VLOWL treatment |
| N06 -> N13 | fixed unique-maximum exact-overlap rule across all 23 partners |
| N13 count 22 -> N23 | established LOW IF EVEN transition |
| Exact N23 final wording | **absent from surviving source** |

No per-word choices, phrase grammar, synonym palette, alternate overlap threshold or target-facing selection is introduced.

## Relation to prior work

Earlier work already knew several individual ingredients:

- N06/N13 share lamp-scene vocabulary;
- N13 participates in the count-line graph;
- SEATS and KEEPER independently select N23;
- the AT/MT/ET/PT chain reconstructs the fixed N20 payload;
- VLOWL is reduced as a whole token with LOW BIT.

The new contribution is the **composition** from the completed address chain itself into N06, then through the same maximal-overlap operator into N13 and the existing count transition into N23. It turns three previously separate K08 subprograms into one target-blind lineage.

The N06 literal wording is already known not to be K08, and broad N06 edit/deletion families are prior commitment-negative work. This result therefore does not justify reopening those phrase families.

## Consequence

The fixed source program now reaches:

1. the complete N20 semantic payload;
2. a source-labelled Emily second draft, N06;
3. an independently selected later Emily narrative, N13; and
4. the final-margin witness, N23.

The remaining missing edge is much narrower: **the exact authored text/version operation after this lineage**, not which broad scene or draft family to search.

K01/K02/K03/K05/K06/K07 remain accepted. K04 and K08 remain missing; REC8/1 remains incomplete.

## Reproducer

`agents/agent14/k08_n06_n13_n23_overlap_lineage_sft.py`

The source-pinned SFT reproduces the entire chain, exhausts all 23 N06 overlap partners, enumerates all 276 note-pair overlap lengths as a corpus control, checks the N13 count transition and reads neither K08 nonce nor acceptance data.
