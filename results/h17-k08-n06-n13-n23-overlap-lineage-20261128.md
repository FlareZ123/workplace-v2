# K08: address-head-selected N06 interlocks with the independently selected N13/N23 route

**Agent 14 | 28 November 2026 | target-blind cross-program interlock | final wording still unresolved**

> **Same-invocation correction:** the first version of this note described a direct “N06 -> choose strongest overlap partner -> N13” lineage. That wording was too strong: scanning all 23 partners and choosing the maximum would introduce a new partner-selection rule. The corrected claim below treats the 23-partner scan only as a **specificity control**. N13 and N23 are selected independently by the pre-existing N09 heading TAILBIT/LEN route.

## New address-head branch: AT/MT/ET/PT -> N06

The fixed K08 overlap decoder uses the ordered addresses:

`AT -> MT -> ET -> PT`

Their changing first coordinate is **AMEP** and invariant second coordinate is **TTTT**.

Using only established operations:

1. LOW BIT(`AMEP`) = **7**, selecting N07, the independently calibrated reversal instruction.
2. LOW BIT(`TTTT`) = **0**, outside the N01..N24 namespace.
3. A1Z26 `AMEP` addresses N01/N13/N05/N16.
4. Their normalized post-label word counts are **11/22/14/11**.
5. Under the established A=0 count alphabet, those counts emit **LWOL**.
6. N07 reversal gives **LOWL**.
7. Apply the established whole-token LOW BIT reduction: LOW BIT(`LOWL`) = **6**.
8. N06 is Emily's source-labelled **Second desk draft**.

This branch reads no K08 nonce, commitment or candidate phrase.

## Independent N13/N23 branch already fixed by prior work

The existing tokenizer-independent N09 heading route independently selects:

- **N13** through its TAILBIT result followed by LOW IF EVEN; and
- **N23** through the heading LEN result.

That route predates this result and does not depend on the new N06 address-head construction. See [N09 heading TAILBIT/LEN lineage](h17-k08-n09-heading-tailbit-len-lineage-20261128.md).

N13's 22-word body also independently reproduces the established count transition `22 -> 23` under LOW IF EVEN.

## N06/N13 exact-overlap interlock

Now compare the **already selected** N06 and N13 bodies. Their unique maximal exact contiguous common span has:

- length **3 normalized words**;
- SHA-256 `2ab57327d0317a1f28546095fb2cccbafc190fd90d4bbff5f19a64637d6a3e8f`.

As a specificity control only, compare N06 against every other numbered note:

- partner denominator: **23**;
- N13 is N06's unique strongest exact-overlap partner;
- across all **276** unordered note pairs, exactly one pair has maximal overlap length 5, none length 4, and two pairs length 3.

The public report records the span fingerprint rather than reproducing the source phrase.

## LEN closes a desk-draft / photograph loop

Apply the already-emitted **LEN** operator to the independently observed three-word N06/N13 common span:

`LEN = 3 -> N03`

N03 is source-labelled **Kitchen photograph**.

N03 has **12** normalized post-label words. Apply the established LOW IF EVEN count transition:

`12 -> 13 -> N13`

So the combined source-only interlock is:

`AT/MT/ET/PT -> AMEP -> N07 -> LWOL -> LOWL -> N06 Second desk draft`

while the independent heading branch selects N13/N23, and the cross-check:

`N06 + N13 common span -> LEN 3 -> N03 Photograph -> count 12 -> LOW IF EVEN -> N13`

returns to the independently selected N13.

This is notable because MAIL-11 says Emily worked out the keeper wording from **desk notes and photograph captions**. The interlock lands on exactly those two retained source-role classes without using target data. That semantic agreement is corroboration, not proof of a historical edit edge.

## Source-vs-free ledger

| Step | Status |
| --- | --- |
| AT/MT/ET/PT and order | fixed by independent cross-carrier payload decoder |
| AMEP vs TTTT | source-discriminated by valid-note LOW BIT 7 vs invalid 0 |
| AMEP -> N07 | fixed LOW BIT |
| AMEP -> note counts -> LWOL | fixed A1Z26/count mapping |
| N07 reversal -> LOWL | independently calibrated |
| LOW BIT(LOWL) -> N06 | established whole-token reduction, matching prior VLOWL treatment |
| N13/N23 selection | **independent prior N09 heading route**, not chosen by N06 overlap |
| N06/N13 span | measured relation between two already selected notes |
| 23-partner N06 maximum scan | specificity control only; **not a selector** |
| LEN(span)=3 -> N03 | established LEN/A1Z26 operation |
| N03 count12 -> N13 | established LOW IF EVEN count transition |
| Exact final wording after N23 | **absent from surviving source** |

## Consequence

The strongest new claim is not a new phrase candidate. It is a cross-program interlock:

- the completed N20 address decoder independently selects **Emily's N06 second desk draft**;
- the separate heading program independently selects **N13 and N23**;
- the selected N06/N13 pair is joined by a rare exact overlap whose length selects a **photograph** record and loops back to N13.

This connects the deterministic payload program to the exact source-role classes MAIL-11 names as wording inputs, while leaving the actual final wording unguessed.

Do not reopen N06 synonym/deletion grammars or treat the N06 partner scan as a historical selector. The missing edge remains a source-fixed authored version operation from these selected inputs to the exact keeper-envelope inscription.

K01/K02/K03/K05/K06/K07 remain accepted. K04 and K08 remain missing; REC8/1 remains incomplete.

## Reproducer

`agents/agent14/k08_n06_n13_n23_overlap_lineage_sft.py`

The source-pinned SFT reproduces the address-head N06 selector, measures the N06/N13 overlap, exhausts all 23 N06 partners and all 276 note-pair overlap lengths as controls, closes LEN=3 onto N03 and the N03 count transition back to N13, and reads neither K08 nonce nor acceptance data.
