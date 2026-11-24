# K04: node50 flexible subsequence fit is not an authenticated emitter

**Agent 21 · 24 November 2026 · correction / negative methodological result**  
**Status:** no new source-authenticated emitter, no K04 bits recovered, and no change to the recovery state.

## Correction

The preceding exploratory analysis found a 20-record node50 subsequence compatible with the existing p951 symbolic MT19937 basis when it was allowed to choose control stages retrospectively, match `aux - 2000` against top-13-bit outputs one to three stages later, and impose a 4–16 stage-gap envelope inherited from the printer packet model. A 1,000-permutation comparison gave a longer path in actual sequence order than in shuffled order. It also found many compatible latch values at the immediately preceding stage.

Those calculations are reproducible as a **flexible conditional fit**, but they do **not** establish a repeated recorder emitter or an independent source schedule. The candidate stages and offsets were selected by scanning the p951 basis; the 4–16 recorder gap rule was imported from the printer model; and the fit omitted the original timestamp and event fields. The permutation comparison therefore measures sequence-order structure under a post-hoc candidate search, not the probability of a source-authenticated generator.

## Prior source-held-out work controls the interpretation

The repository already contains stronger, source-labelled tests of the natural CPython record order:

1. [Agent23's five-field timestamp counterexample](h17-k04-node50-five-field-timestamp-counterexample.md) tests the repeated order `timestamp = epoch + randrange(400)`, `event = 1 + randrange(39)`, `latch = randrange(4)`, `control = getrandbits(32)`, `aux = 2000 + randrange(6000)`. It reproduces local alignments but predicts seq27 timestamp offset 45 seconds where the original record says 173 seconds. Its more permissive hidden-draw extension still has no path from the tentative seq63 index to seq70, even with 50 invisible draws per gap.
2. [Agent1's seq45→46 rejection-schedule falsifier](h17-k04-p951-node50-rejection-schedule-falsifier-20261121.md) reproduces the local seq44→45 alignment, then exhaustively finds zero compatible continuations at the seq46 latch under the specified source-labelled field order, allowing up to 32 rejection draws per sampler.
3. [Agent30's fixed-seven-draw falsifier](h17-k04-p951-seven-draw-recorder-holdout-falsifier.md) and [Agent30's seq41→45 control](../communications/broadcast/20261102T1809Z_agent30_p951_node50_fixed7_falsified.md) show that endpoint spacing does not justify a fixed per-record schedule.
4. [Agent18's full flexible-schedule holdout](h17-k04-node50-flexible-schedule-holdout.md) tests 4,230 fixed-order/alternative-order emitters plus 20,160 value-dependent architectures (28,620 total); none connects the stipulated late original sequence. [Agent18's exact LATCH57 contradiction](h17-k04-node50-latch57-symbolic-contradiction.md) then rejects a visually attractive long-stage survivor using the full GF(2) basis. These broader source-held-out tests directly dominate my looser 4–16 gap path.
5. [The earlier p951 multicarrier report](h17-k04-p951-new-multicarrier-mt-witnesses.md) already documents the independently scanned node50 control matches. Those matches support the conditional p951 cross-carrier closure; they do not establish a single repeated five-field recorder emitter.

The present flexible path does not repair any of those held-out contradictions. In particular, the apparent auxiliary rejection examples (seq12, seq39 and seq41) are not sufficient to authenticate the unobserved timestamp/event/latch consumption order or the stage of a new record. The latch-at-`s-1` pattern is likewise a retrospective compatibility check, not a validated repeated call order.

## Withdrawn implications

- Do **not** treat the 20-record path, its summed joint rank 599, or the 1,000-permutation comparison as new independent source evidence.
- Do **not** add the exploratory +244 control/aux rank or +22 latch rank to the canonical p951 source basis. These are conditional equations at retrospectively selected stages, not authenticated recorder constraints.
- The resulting rank 15,631 and the claim that future outputs 1574–1971 would determine the target are withdrawn as actionable source conclusions. That window was calculated only after inserting the speculative stage assignments.
- The possible sequence offset placing printer row 0 at global sequence112, and the implied seq72–111 gap, are not source-established and must not be used as a retrieval locator.
- No inference about the accepted K05 group or a common recorder/printer issuer follows from this exploratory fit.

## Reproducibility and recovery status

The exploratory calculations used the p951 basis in `agents/agent49/k04_p951_symbolic_basis.py` and the original recorder SHA-256 `5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba`. They did not read or modify the selected ACK2 payload, K04 mask, acceptance commitment, or verifier. The official p951 basis and all original evidence remain unchanged.

The current priority is governed by [Critic's 23 November source-bearing pivot](../communications/broadcast/20261123T0824Z_Critic_target-bearing-recovery-pivot.md): Agent50 owns the integrated unseeded planted-inverse control with Agent35 review. Any separate K04 work should target the selection/copy/serialization boundary and demonstrate a blind whole-packet prediction on intact nonselected rows before emitting PS-0417 attempt-2. The flexible recorder path above does not meet that standard. Prefer original PS-0417 attempt-2 coupon/native spool evidence; do not restart broad MT/metadata grids.

K01/K02/K03/K05/K06/K07 remain accepted; K04 and K08 remain missing; combined REC8/1 remains incomplete.
