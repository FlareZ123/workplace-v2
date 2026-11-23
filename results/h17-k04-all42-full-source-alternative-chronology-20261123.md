# K04: exact full-original-source alternative MT stage chronology, with a target-facing exclusion

**Agent 11 | 23 November 2026 | Complete original-source GF(2) positive, no original K04 commitment hit.**

## Question and original-source boundary

Does a proposed single-stream native MT19937 chronology that fits **all 42** previously identified original MT word witnesses also reproduce every other intact historical printer packet, or can source-compatible schedules yield additional target information without using the untrusted 18:02 ACK2 copied payload?

Input is the unchanged original `resources/evidence/print/spool-reconstruction.log`, SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. The target is row129, `2026-10-03T18:02:00Z PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER`. Its 16-byte `PAYLOAD` is **not decoded**. The 132 other packets supply 528 original 32-bit little-endian native MT words after exact untempering.

The producer and chronology remain *conditional*. The archive does not authenticate MT19937 printer firmware, draw counts, retransmission reuse, or the target's emission index.

## New fully consistent chronology

The [single runnable source-pinned SFT](../agents/agent11/k04_all42_fullsource_alternative_sft.py) freezes a **133-row alternative stage schedule** (entire vector in code), maintaining all 25 complete native recurrence witnesses and all 17 source-matched 31-bit firstword witnesses. Every non-REQUESTED gap is 4..16 draws. REQUESTED rows are admitted at 0..4 draws, as in the prior all-42 stage model.

Unlike witness-only stage feasibility, this reproducer builds the complete 19,968-dimensional native MT19937 bit-linear state and inserts **all 16,896 original known bit observations**. It verifies **zero inconsistent equations, source rank 15,434**, and 42/42 original observed word witnesses. This is a genuinely source-consistent alternative to the previously published p951 chronology's rank 15,365, rather than a timetable satisfying selected witnesses while contradicting the other packets.

The source-stage search included a decisive screening correction. The plain 42-witness graph plus direct full and firstword recurrences admitted apparent candidates that the complete GF(2) source rejected. Two extra exact necessary relations expose early failures even when the intermediate native outputs are missing:

- Missing the word at `t+1` does **not** hide the native bit30 identity `bit30(X[t+624] XOR X[t+397]) = bit31(X[t])`.
- The second-order fourword relation at `(t, t+227, t+396, t+850)` fixes 31 bits of the fourth output from the first three; the distinct `(t, t+227, t+397, t+851)` relation fixes its bit30.
  
Those direct structural tests narrowed the search; the **entire original-source GF(2) basis** is the final judge. The SFT verifies that final judge, rather than treating local recurrence checks as sufficient.

## What this predicts for K04 and why it is already excluded

The alternative schedule places:

| Historical printer row | Relative native MT stage | Status |
| --- | ---: | --- |
| row128, 18:01 attempt1 `REQUESTED` | 951 | Original copied packet is retained |
| **row129, 18:02 attempt2 `ACK`** | **952** | **Withheld selected coupon** |
| row130, 18:03 attempt3 `REQUESTED` | 957 | Original copied packet is retained |

The exact whole-source target projection has **32 independent unknown bits out of 128**; the first three 32-bit output lanes are forced by overlap with the retained attempt1 packet's last three lanes. Under the fourword little-endian serializer, the complete hypothetical original **raw coupon** family is

```text
6ADB2FB180DA2AA90B33F7A4????????
```

where the last four bytes are a single arbitrary uint32, and the first 12 bytes come **directly from original row128**, not guessed or inferred from target hash. This particular complete `2^32` candidate family was **already exhaustively tested** against the official unmodified K04 mask and full SHA256 commitment by [Agent21's adjacent shifted-output search](h17-k04-adjacent-shift-one-word-exhaustive.md), with independent planted complete-coupon positives, and yielded **zero original matches**. The present investigation does not rerun those 4,294,967,296 digests and does not claim their negative as a newly measured result.

Therefore, **this exact source-consistent chronology cannot recover an accepted K04 under its selected 952/output-overlap interpretation**. An exact match of all intact MT words alone is insufficient to establish the historical selected emitter. The 18:01 REQUESTED stage advances only one draw before the later 18:02 ACK even though a complete REQUESTED 16-byte buffer is retained. Such payload reuse/overlap has no independent historical evidence and could violate a literal four-fresh-output physical printer model.

## Decision consequence

The new asset is an **independently reproducible all-intact-packet source-consistent alternative stage vector** with exact target freedom, supplying a concrete counterexample to treating a source-consistent native MT chronology as uniquely determined. Future genuinely new printer models should pass the full 528-word GF(2) system, a frozen historic complete-object control, and the original **whole** K04 commitment, with no dependence on the copied selected ACK2 bytes. A merely stage-feasible model should be rejected before expensive hashing; conversely, a fully source-consistent model can still be rejected by the target commitment when it implies an already exhausted coupon family.

**Original recovery remains unchanged:** K01/K02/K03/K05/K06/K07 PASS, K04/K08 MISSING, combined REC8/1 INCOMPLETE. K04 independently authenticated physical bits remain 0/128; exact K08 author-final words remain absent. No source, official verifier, acceptance commitments or canonical candidate changed.
