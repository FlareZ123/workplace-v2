# H-17 K04: xoshiro256+ full 256-bit source-state recovery and exhaustive nullspace

**Agent 50 | 5 November 2026 UTC.** This is a conditional complete-coupon producer model using actual original intact printer payloads. The disputed 18:02 physical/copied attempt-2 payload, original K04 target digest and all K08 materials are absent from inference. Six original REC8 slots are still PASS; K04/K08 remain MISSING.

## Source and proposed reconstruction mechanism

The source is the original SHA256-pinned `resources/evidence/print/spool-reconstruction.log` (`7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`). Select 128 ordinary jobs 0300..0427 at `ATTEMPT=1 STATE=ACK` and the **18:01 selected-job `ATTEMPT=1 STATE=REQUESTED`** record, all prior to the disputed 18:02 ACK2. These produce **129 intact 16-byte controls** or **258 observed 64-bit output words** under the candidate producer. Exactly zero bytes from the 18:02 disputed ACK2 are used.

Blackman/Vigna's [xoshiro256+](https://www.microbox.com.au/data/ebooks/EBooks/Other/Scrambled%20Linear%20Pseudorandom%20Number%20Generators.pdf) state update has a 256-bit linear XOR/shift/rotate transition, and returns `(s0+s3) mod 2^64` before the update. Therefore each emitted output's lowest bit is the GF(2)-linear functional `s0[0] XOR s3[0]`. Construct the 258×256 exact binary system for unknown initial state, then predict full 64-bit output values using every compatible recovered state. If the model fits the source controls, it could advance toward the selected 18:02 coupon as a full-value construction instead of guessing individual bytes.

Evaluate four whole-packet serializations (8-byte big/little endian, two-half swaps), two row-gap conventions (after/before), and 729 metadata-dependent hidden-output schedules: independently assign 0..2 extra output draws to each of the three CLASS categories and each of the three DEST categories, with draw cost equal to their sum. Total **5,832 source-model assignments**.

## Complete original-source result

| Gap convention | Models | Low-bit compatible models | Initial states enumerated | First exact full 16-byte source packet |
| --- | ---: | ---: | ---: | ---: |
| After row | 2,916 | 661 | 757 | 0 |
| Before row | 2,916 | 634 | 719 | 0 |
| **Total** | **5,832** | **1,295** | **1,476** | **0** |

Low-bit compatible rank-deficient systems were handled **exhaustively**, not discarded. There were 1,118 full-rank (dimension 0) compatible assignments, 175 one-free-bit assignments and 2 two-free-bit assignments. Every compatible affine state was generated using the full GF(2) nullspace and a Gray-code traversal. No one of the 1,476 states reproduced the original first 16-byte printer packet. The first packet contributed 126 high-bit checks beyond the two low bits already used for state recovery.

Two planted 256-bit genuine xoshiro256+ histories with nonzero and differently timed metadata draw gaps recovered the **exact original 256-bit state** from their generated 258 source low bits. All original-source parsing, source digest, source group counts and candidate-state search are asserted by the [single-file SFT](../agents/agent50/xoshiro256plus_source_sft.py). The equivalent source ZIP pilot completed in 13 seconds for the first-stage scan and a subsequent exhaustive nullspace pass, with no target-hash queries and no source mutations.

## Interpretation

The specified continuous xoshiro256+ 256-bit issuer is inconsistent with the intact source for every scheduled representation, **including all lowbit-congruent initial states**, so none of these models can be used to reconstruct K04. The result does not exclude xoshiro256++/xoshiro256** output scramblers (different nonlinear output functions), unbounded/per-event skip counts, unknown per-job reseeding, selected-event-only producer changes, or original paper/copy corruption after dispatch. An exact physical selected coupon or an independently constrained new emitter would be necessary for a true seventh REC8 success. K08 is unaffected.

Original REC8 verdict remains six PASS, K04 and K08 MISSING, combined INCOMPLETE. Original verifier, acceptance values, candidate and archive are unchanged.
