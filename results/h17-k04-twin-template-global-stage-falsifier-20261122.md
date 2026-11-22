# K04 repeated-lane witnesses do not transfer to the selected row under a global stage schedule

**Date:** 22 November 2026  
**Scope:** independent source-pinned review of the four held-out MT lane-word matches in `h17-k04-source-witness-variable-lane-mosaic-20261122.md`.  
**Question:** do the four apparent held-out successes define an authentic lane selector for selected spool row 129 (PS-0417 ACK2), or are they dependent historical repetitions whose stage schedule does not transfer?

## Result

The four matches are **two duplicated recurrence signatures**, not four independent validations. Both signatures occur twice in historical triplets shifted by four rows:

| Signature | Historical triplets | Required stage gaps |
|---|---|---|
| `(54,84,p=1,i=1,q=2)` | `(8,62,92)`, `(12,66,96)` | `S_k-S_r=396`, `S_l-S_r=622` |
| `(54,84,p=2,i=2,q=3)` | `(8,62,92)`, `(12,66,96)` | `S_k-S_r=396`, `S_l-S_r=622` |

The selected row's matching raw-row geometry is `(45,99,129)`. But matching row offsets `(54,84)` is not enough: the source-constrained global stage model does not permit any of the 23 historical signatures to transfer to row 129.

## Reproduction

The attached script `agents/agent18/k04_twin_stage_falsifier.py` independently:
1. SHA-pins the original `spool-reconstruction.log` (`7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`).
2. Withholds selected row 129 and untempers the 132 intact 16-byte packets as little-endian MT19937 words.
3. Re-discovers **25** historical recurrence witnesses and **23** distinct signatures; the only repeated signatures are the two twins above.
4. Builds the 50 historical stage-sum equalities. For witness `(r,p,k,i,l,q)`:
   - `S_k-S_r = 396+p-i`
   - `S_l-S_r = 623+p-q`
5. Solves an integer stage-draw model `S_j = sum(w_0 ... w_{j-1})` with a deliberately broad, source-sensitive bound: payload-bearing ACK rows consume **4–100** MT outputs; REQUESTED rows may consume **0–100**. This does not assume REQUESTED means no generator consumption.

The historical system is feasible. Under these bounds, the target intervals are:

- `S_99-S_45 = 398..487`; the repeated twins require **396**.
- `S_129-S_45 = 550..613`; every one of the 23 signatures requires **621..626**.

Therefore **0/23** signatures can be transferred to the target while preserving one global stage schedule. The decisive second-gap shortfall is at least eight draws, even at the most permissive target bound.

## Global-schedule positive control and sensitivity

The existing p951 schedule from `agents/agent49/k04_p951_symbolic_basis.py` is a constructive positive control for the historical equations: it satisfies all 25 witnesses, places `S_129=951`, and gives the target triplet gaps **401/609**, not the twin requirement **396/622**. The script verifies this schedule and a solver positive control using those actual target gaps.

As a stress test, allowing **every** row, including payload-bearing ACK rows, to consume 0–100 draws makes 4/23 signatures feasible. All four end at output lane `q=3`; neither repeated twin is among them. This is not the primary model because a direct 4-word ACK payload cannot consume zero MT outputs. It demonstrates the boundary of the conclusion rather than rescuing the twin lane selector.

## Interpretation

- The four held-out words are dependent: each repeated signature is observed twice in the same +4-row-shifted geometry.
- The historical recurrence itself remains a real, reproducible pattern in the source packets.
- The repeated twin signatures are **not** a source-authenticated lane selector for PS-0417. Their two-lane target predictions must not be promoted to coupon bytes; the 960 row-offset-only combinations do not preserve the global stage schedule.
- The p951 model is a coherent historical schedule, not proof that the printer actually used MT19937. The result is conditional on a single global MT19937-like stream and direct 32-bit word consumption by payload-bearing ACK rows. It does not exclude a different generator, multiple streams, or a non-MT serializer.

## Decision-changing consequence

Retain the historical recurrence as a diagnostic, but close the repeated-twin-to-target transfer. Further progress needs a native PS-0417 queue/render object or a source-authenticated host-stage/serialization manifest that fixes the selected row's actual producer schedule. Do not repeat the 960 per-lane mosaic or treat the two predicted tail words as accepted evidence.

**Confidence:** high for the finite stage-feasibility result under the stated model; no conclusion about the true printer producer outside that model.
