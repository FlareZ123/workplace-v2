# K08: AT/MT/ET/PT address heads select N07 and continue to the N23 final-margin carrier

**Agent 14 | 28 November 2026 | target-blind source-program extension | final wording still unresolved**

## Question

The completed N20 payload decoder now uses the fixed ordered address sequence:

`AT -> MT -> ET -> PT`

Can that address structure itself select the next operator and carry the program from the fixed semantic payload toward the known N23 final-version record without consulting the K08 commitment?

## Fixed address-coordinate selector

The four addresses have one invariant coordinate and one changing coordinate:

- first letters: **AMEP**
- second letters: **TTTT**

Apply the already-established ASCII LOW BIT packing, first bit as LSB:

- LOW BIT(`AMEP`) = **7**, selecting **N07**;
- LOW BIT(`TTTT`) = **0**, outside the N01..N24 note namespace.

The address order is already fixed by the independent AT/MT/ET/PT decoder. No address permutation or target-guided coordinate choice is introduced. The changing coordinate is the only one that yields a valid numbered note, and N07 is the previously calibrated reversal instruction used by the AES -> SEA source loop.

## Count image and reversal

Read the four changing address letters by the same A1Z26 note namespace:

- A -> N01
- M -> N13
- E -> N05
- P -> N16

Their normalized post-label word counts are:

`11 / 22 / 14 / 11`

Under the established A=0 count-to-letter convention this emits:

`LWOL`

Apply the N07 reversal selected immediately above:

`LWOL -> LOWL`

The result begins with the independently established literal operator **LOW**, leaving one residual symbol **L**.

## Residual transition to N23

Interpret residual L in the same A1Z26 note namespace:

- L = 12;
- established LOW IF EVEN sends 12 -> **13**, selecting N13;
- N13 has 22 normalized post-label words;
- applying the same LOW IF EVEN transition sends 22 -> **23**, selecting N23.

N23 is the Emily-authored record that explicitly refers to the words she finally put in the margin / on the keeper envelope.

The complete target-blind lineage is therefore:

`AT/MT/ET/PT -> AMEP -> LOW BIT 7 -> N07 reverse -> LWOL -> LOWL -> LOW + L -> L(12) -> LOW IF EVEN -> N13 -> count 22 -> LOW IF EVEN -> N23`

## Source-vs-free decision ledger

| Step | Status |
| --- | --- |
| AT/MT/ET/PT and order | fixed by the independently reconstructed payload decoder |
| Choose changing address coordinate | source-discriminated: AMEP maps to valid N07 while invariant TTTT maps to 0/outside note namespace |
| AMEP A1Z26 note IDs | fixed |
| Note counts 11/22/14/11 | fixed source values |
| Count-to-letter A=0 | established source-program convention |
| N07 reversal | selected by AMEP LOW BIT and calibrated independently |
| Parse LOWL as established LOW operator + residual L | source-literal operator-prefix interpretation; no acceptance data used |
| LOW IF EVEN on L and then N13 count | established operator reused twice |
| N23 destination | emitted by the above chain; not selected from K08 acceptance |
| Exact N23 author-final wording | **still absent from surviving source** |

The one interpretive step that remains less direct than the numeric transitions is treating the emitted `LOW` prefix in `LOWL` as the already established operator and carrying the one-symbol residual forward. The source does not contain a formal grammar statement saying to split tokens this way.

## Controls and prior art

The source-pinned reproducer checks the exact address columns, note IDs, note counts, `LWOL -> LOWL`, residual L, both LOW-IF-EVEN transitions and the presence of N23's final-margin vocabulary. It reads neither the K08 nonce nor the acceptance commitment.

Repository search for the combined `AMEP LWOL LOWL N13 N23` chain returned no prior result. Earlier work separately established the AT/MT/ET/PT payload, N07 reversal, LOW/LOW-IF-EVEN vocabulary, N13 lineage and N23 final-margin role; the new contribution is the target-blind composition from the completed address chain through those operations to N23.

## Consequence

This materially advances the fixed K08 source program: the completed payload decoder no longer dead-ends only at the 13-word N20 semantic brief. Its own address structure selects a known operator and reaches the correct **final-version carrier class, N23**, without reading K08 target data.

It still does **not** recover the missing author-final sentence. N23 confirms that the exact words existed but does not quote them. Do not convert this locator advance into a new phrase grammar. The decisive remaining edge is a source-fixed text emitter/version operation at or beyond N23 that yields the complete normalized final wording.

K01/K02/K03/K05/K06/K07 remain accepted. K04 and K08 remain missing; REC8/1 remains incomplete.

## Reproducer

`agents/agent14/k08_address_heads_to_n23_sft.py`

The script uses only the pinned crew-note source and reports operator/selector IDs and aggregate tokens. It reads no K08 nonce, acceptance target or candidate wording.
