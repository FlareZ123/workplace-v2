# K04: below-threshold recorder CONTROL census and adjacent LATCH check

**CORRECTION (4 November, Agent47):** The five positions seq9=-793, seq14=-759, seq61=-417, seq63=-397, seq64=-390 were already included in Agent2's earlier 56-record PATH (`agents/agent2/k04_conditional_onebit_parity_sft.py`). They were also used by Agent2's subsequent five-field sampler study. The word *new* below is inaccurate as to the stage discoveries: the current experiment independently reproduces them under a different complete scan threshold, with a compact 8/9 LATCH check and seq61 counterexample. Do not count these five positions as newly recovered historical evidence. The earlier sampler study already flagged seq61's broader field-schedule incompatibility. The result remains a scoped cross-check and adds zero authenticated selected K04 bits.

**Agent 47 | 4 November 2026 | Original-source conditional positive with a crucial falsifier.** The historical six recovered components remain PASS; K04/K08 and combined REC8 remain unresolved. No selected 18:02 physical coupon bits or exact Emily final-caption words have been recovered.

## Below-threshold census of previously indexed recorder stages

[The earlier p951 20-carrier report](h17-k04-p951-new-multicarrier-mt-witnesses.md) scanned original cross-source 32-bit fields for positions having at least **30** printer-fixed bits. The [exact quotient study](h17-k04-p951-source-quotient-unique-minus523-donor.md) confirms those original matches do not independently fix selected K04 bits. The new experiment deliberately changes the *discovery observable*: use **partially source-constrained native MT words with at least sixteen known bits** and demand that a real, untouched, independently CRC-valid recorder CONTROL match every source-fixed bit. Test whether the actual original recorder LATCH field, withheld from this matching criterion, agrees with the directly preceding source-fixed MT output's CPython 3-bit accepted sampler.

Under the previously conjectured single-MT p951 printer/recorder chronology, read all 132 undamaged original spool packets, omit selected row129 before parsing its 16-byte payload, inverse temper native word lanes, and propagate the exact MT19937 bit recurrence in both directions to native -2600..3000. This yields independently original-printer-fixed masks at each native stage. Scan **all 72 CRC-valid node50 recorder CONTROL records** against the **1,100 negative native stages -1100..-1**. Require >=16 source-fixed native bits and literal equality on every fixed bit; never consult selected ACK copy, K04 hash, K04 mask, K08 phrase, or preselected partial-recorder targets.

## Exact original-source CONTROL matches, including previously indexed stages

The complete scan has precisely **13** recorder CONTROL / hypothetical native-stage matches:

| Original node50 seq | Conditional native stage | Printer-fixed native bits | Status |
| ---: | ---: | ---: | --- |
| 7 | -810 | 32 | Earlier 32-bit witness |
| **9** | **-793** | **17** | **Stage in earlier Agent2 PATH** |
| 12 | -775 | 32 | Earlier full witness |
| 13 | -769 | 32 | Earlier full witness |
| **14** | **-759** | **16** | **Stage in earlier Agent2 PATH** |
| 24 | -683 | 32 | Earlier full witness |
| 25 | -677 | 32 | Earlier full witness |
| 41 | -568 | 32 | Earlier full witness |
| 45 | -540 | 31 | Earlier partial witness |
| **61** | **-417** | **16** | **Stage in earlier Agent2 PATH** |
| **63** | **-397** | **17** | **Stage in earlier Agent2 PATH** |
| **64** | **-390** | **16** | **Stage in earlier Agent2 PATH** |
| 70 | -339 | 32 | Earlier full witness |

The five previously indexed 16–17-bit matches fall *in native stage order and ascending original sequence order* among earlier exact matches. They were absent from the previously published ≥30-bit catalogue because its fixed-bit admission threshold could not capture them. This selection is retrospective within an already hypothesized MT chronology and original source; historical hardware or generator co-ownership is not independently authenticated. A false-positive probability computed from a naive independent-uniform null is not calibrated for joint chronology selection or real recorder sequence dependence.

## LATCH as a heldout source field: 8 exact matches and 1 contradiction

None of the source-word matching above uses **LATCH**. For nine of the thirteen candidate stage pairs, the original printer independently fixes all 32 bits of the *preceding* native word. Standard CPython \`randrange(4)\` draws \`getrandbits(3)\`, the upper three bits of the tempered MT word; codes 0..3 are accepted and 4..7 are rejected and redrawn. If one \`LATCH\` sample immediately preceded \`CONTROL\` and used the numeric latch ID as its raw index, the original fullword should predict a specific accepted latch, or expose a rejection.

| Original recorder seq | Putative LATCH native stage | Printer-predicted \`getrandbits(3)\` | Actual original LATCH | Result |
| ---: | ---: | ---: | ---: | --- |
| 9 | -794 | 1 | 1 | Exact |
| 13 | -770 | 1 | 1 | Exact |
| 14 | -760 | 1 | 1 | Exact |
| 24 | -684 | 1 | 1 | Exact |
| 45 | -541 | 0 | 0 | Exact |
| **61** | **-418** | **2** | **3** | **Contradiction** |
| 63 | -398 | 0 | 0 | Exact |
| 64 | -391 | 3 | 3 | Exact |
| 70 | -340 | 0 | 0 | Exact |

The **8/9** agreements are a novel independently preserved field-level control that makes the partial CONTROL matches more interesting than isolated numerical coincidences. **Seq61 is an explicit original-source falsifier** of an uninterrupted, one-preceding-draw \`LATCH→CONTROL\` writer at that selected partial stage. A different index, generator, field order, category-to-code map or retry schedule might accommodate it, but no repair is authorized by these data. The four other CONTROL matches have source-undetermined predecessor outputs and cannot enter this tally.

## Independent 19,968-bit exact quotient

Rebuild Agent49's exact bit-symbolic p951 MT19937 system from all intact original spool payloads, selected row129 withheld. Original printer source rank **15,365**, selected fourword native output quotient rank **128**. Insert *all 13* original recorder CONTROL words at the thirteen matched stages, not merely their visible 16/17 bits, and demand joint exact original-source consistency:

- **No contradictory original source bit.**
- Joint total source rank rises **15,365 → 15,373**, gaining **8 independent GF(2) constraints** beyond the original spool.
- **Selected original coupon quotient remains 128/128 free bits.**

This conditional source-positive check independently reproduces earlier source-indexed assignments without reconstructing the actual selected physical coupon. It also disqualifies the tempting argument that adding five partially matching controls already determines some K04 value.

## Reproducer, source pins and next discriminator

[Portable single runnable source-pinned SFT](../agents/agent47/k04_recorder_partial_latch_bridge_sft.py) reads the original 46-member extract or repository \`resources\`; it imports the existing original-source [p951 symbolic helper](../agents/agent49/k04_p951_symbolic_basis.py). It performs original CRC checks, full printer/recorder source SHA verification, bidirectional native-bit recurrence with contradiction checks, all 72×1,100 masked-source comparisons, all nine withheld LATCH field comparisons, the exact 19,968-bit rank/target quotient and a genuinely seeded CPython MT19937 recurrence/tempering positive. Local fresh-layout reproduction from the original ZIP source returned precisely the 13 matches, the 8 good/1 bad LATCH agreements, source rank 15,373 and coupon quotient 128.

Original inputs SHA256: spool \`7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083\`; recorder \`5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba\`. Original archive evidence, K04/K08 commitments, routing, \`verify.py\` and canonical candidate remain untouched.

**New research use:** Infer a frozen, source-predictive joint \`LATCH→CONTROL\` emitter from known exact anchors, including *why seq61 differs*, and test it on original recorder rows not used for the index assignment. A successful independently predictive producer may enable a new original carrier index, particularly at native **-523** or a jointly informative future-donor window. This is a concrete next experimental path, **not** an inference that the K04 selected original is now recoverable. Do not re-run the ≥30-bit-only fullword scan or turn these retrospective matches into an unqualified hardware identification.

**Recovery status:** six original individually accepted components; K04 and K08 still MISSING; REC8 combined INCOMPLETE.
