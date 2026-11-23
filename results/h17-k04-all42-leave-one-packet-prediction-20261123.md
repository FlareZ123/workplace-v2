# K04 all-42 alternative chronology: leave-one-packet-out prediction gate

**Agent 11 | 23 November 2026 | Conditional falsifier; no K04 component recovered.**

## Question

Does the frozen all-42 MT19937 stage chronology predict any intact 16-byte printer packet when that packet is removed from the source basis, or is its full-source consistency only an in-sample fit?

## Method

- Pinned the original `spool-reconstruction.log` at SHA-256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083` and reused the exact 133-row stage vector from [the 23 November all-42 full-source SFT](../agents/agent11/k04_all42_fullsource_alternative_sft.py).
- Excluded selected PS-261003-0417 row129 before decoding its disputed PAYLOAD. No K04 mask, K04 commitment or selected ACK2 payload value was loaded.
- Rebuilt the 19,968-dimensional symbolic MT19937 word expressions and the exact GF(2) source basis. The frozen schedule remains consistent with all 528 intact words at rank 15,434 and reproduces the same 25 fullword plus 17 firstword recurrence witnesses.
- For each of the 132 intact packets, removed all 128 of its source bits, rebuilt the basis from the other 131 intact packets, and projected the held-out packet's four 32-bit words. Counted both fixed bit positions and the independent rank of the remaining output forms. Every fixed bit was compared with the held-out original packet.
- Separately identified the 66 source rows that do not participate in any of the 42 recurrence-witness triples.

Reproducer: [`k04_all42_leave_one_packet_predictive_sft.py`](../agents/agent11/k04_all42_leave_one_packet_predictive_sft.py). Executed locally against the extracted original upload with the Python standard library; no GitHub Actions run is claimed.

## Result

**No complete intact packet is predicted by the other intact packets under this frozen chronology: 0 / 132.**

| Leave-one-out measure | Result |
|---|---:|
| Full 128-bit packet predictions | **0 / 132** |
| Maximum fixed bits in any held-out packet | 127 / 128 |
| Rows reaching 127 fixed bits | 12, 41, 66, 95, 125 |
| Fixed-bit disagreements with original held-out packets | 0 |
| Rows outside every 42-witness triple | 66 |
| Those 66 rows with 0 fixed bits | 54 |
| Those 66 rows with 1 fixed bit | 12 |

Independent free-rank distribution across all 132 held-out packets:

`{1: 5, 32: 2, 33: 10, 63: 6, 64: 6, 65: 18, 95: 3, 96: 3, 97: 13, 127: 12, 128: 54}`.

For the withheld target row129 at its frozen stage952, the same full-source basis fixes 96 bits (the first three words) and leaves 32 independent bits, as already reported. The exact 2^32 target family from that projection was exhaustively tested by Agent21 and is not repeated here.

## Interpretation and boundary

The 15,434-rank full-source consistency result is an **in-sample fit**, not evidence that this alternative chronology predicts a complete independent packet. Even among the 66 rows absent from every recurrence-witness triple, the other packets fix at most one bit of any held-out packet. Do not use this schedule as an authenticated printer producer or as justification for another target-only hash search.

This is conditional on one previously fitted stage vector. It does **not** falsify all MT19937 models, all possible event-stage rules, or a different source-authenticated producer; it shows that this particular full-source alternative has no complete-packet leave-one-out predictive power. A future MT proposal still needs a source-defined stage rule and a complete intact held-out packet prediction before it is promoted.

No source, acceptance commitment, canonical candidate or verifier was changed. K01/K02/K03/K05/K06/K07 remain PASS; K04/K08 remain MISSING; REC8/1 remains INCOMPLETE.
