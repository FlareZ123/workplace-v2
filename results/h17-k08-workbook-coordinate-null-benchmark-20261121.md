# K08 workbook-coordinate null benchmark

**Agent 1 · 21 November 2026 · source-blind specificity check · no phrase recovered**

## Question

The K08 workbook-coordinate convergence report maps the accepted K01 byte pairs to eight A1-style cells and finds an independent M10 equality between a note/seal path and the K05 LOW-IF-EVEN alternate retry stratum. The Critic correctly identified that the A1-cell interpretation needs a source-blind specificity control.

This benchmark reads only the surviving source records. It does not read acceptance.json or the K08 HMAC commitment.

## Actual source observations

- The K01 sequence is 049AAB2E1CDE7A82CD7C60234303C91A. Under the report's row-byte / column-byte convention, it yields EX4, AT171, HN28, DZ122, DT205, AI96, C67, Z201.
- All eight are valid BIFF8 A1 addresses. Under a null of independent uniform bytes, however, any adjacent pair is valid whenever both bytes are nonzero. The probability that all 16 bytes are nonzero is \((255/256)^{16}=0.9392980959\). Therefore, the eight-valid-cells observation alone is weak evidence; it is expected for roughly 94% of random 16-byte blocks under this mapping.
- The K05 source has two CRC-valid 32-bit candidate words per latch. Their four byte-LSBs form these nibble pairs, in latch order: [10,3], [0,0], [13,3], [1,4].
- The source-derived LOW-IF-EVEN rule selects low/high/low/high (mask 1010), yielding nibbles [10,0,13,4], which encode row 10 / column M = M10. The independent note/seal path also yields M10.
- Across all 16 retry masks there are eight unique outputs. M10 is produced by masks 8 and 10; latch 1 has the same target nibble in both alternatives. The official greatest-sequence K05 reducer remains distinct and yields C3, not M10.

## Null probabilities

Assume independent uniform 4-bit nibble candidates for each of four latches.

| Observation | Exact null probability | Interpretation |
|---|---:|---|
| Eight K01 row/column pairs all valid | 0.9392981 | Not surprising by itself |
| Fixed LOW-IF-EVEN mask yields the independently derived M10 | 1/65,536 = 0.00001526 | Relevant only if the rule was specified independently of the output |
| Any of 16 masks yields M10 | 0.00021502 | Appropriate conservative adjustment if masks were searched post hoc |
| M10 appears in exactly two masks | 0.00002515 | Descriptive post-hoc property; do not count as independent evidence |
| Exactly eight unique outputs | 0.2059937 | Not unusual |

If the K01 validity event and the fixed-mask M10 event are treated as independent, their joint null probability is about 0.00001433. If the mask was selected after looking across all 16 outputs, the corresponding joint rate is about 0.00020197. These are conditional model calculations, not formal p-values: the row/column convention and LOW-IF-EVEN selection chronology must be independently justified before using the smaller figure.

A deterministic 1,000,000-trial Monte Carlo run (seed 20261121) gave:
- K01 all-eight-valid: 939,453 / 1,000,000
- fixed-mask M10: 10 / 1,000,000
- any-mask M10: 202 / 1,000,000
- M10 in exactly two masks: 24 / 1,000,000
- exactly eight unique outputs: 206,096 / 1,000,000

The simulation is consistent with the analytic rates at this sample size.

## Assessment

The eight K01 A1 addresses are not, by themselves, persuasive evidence for a workbook carrier. The M10 convergence is materially more interesting because the note/seal path and the K05 LOW-IF-EVEN alternate stratum are separate source paths. Its strength depends on whether LOW-IF-EVEN was genuinely specified from source material before the low-bit output was examined. The alternate K05 stratum is not the official K05 component, so M10 remains a conditional workbook locator, not a recovered component.

The missing mug-stock.xls remains a high-value acquisition target. If an authorized native copy is obtained, inspect M10 and C3 first, then the eight K01-derived cells, and preserve original BIFF bytes, comments, hidden sheets, formulas, formatting, and OfficeArt anchors. Do not treat the conditional P212 branch or WRAPT wordplay as evidence in this null calculation.

**Recovery status unchanged:** K01/K02/K03/K05/K06/K07 accepted; K04 and K08 remain missing; no final phrase recovered.

## Reproducer

agents/agent1/k08_workbook_coordinate_null_sft.py verifies source hashes, reconstructs the actual K01/K05 observations, calculates the exact null probabilities, and runs the seeded Monte Carlo without consulting any acceptance commitment.