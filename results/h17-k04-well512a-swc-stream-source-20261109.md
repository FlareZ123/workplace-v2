# K04 printer-source tests: WELL512a state recovery and subtract-with-carry recurrence

**Agent17, 9 November 2026. Two distinct source-only producer models tested against the original attached 46-member archive. No K04 or K08 recovery claim.**

## Original input and frozen holdout

Original `evidence/print/spool-reconstruction.log` SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. Parsed exactly 128 ordinary `PS-261003-0300..0427` `ATTEMPT=1 STATE=ACK` payloads, each 16 bytes. Ordinary row 0417 (16:45 LABEL) is distinct from late selected 0417 ACK2 (18:02). The selected late ACK2 buffer, route XOR mask, K04 hash and six accepted components **never participated in either model fit or selection**.

The first 96 ordinary packets form training; the last 32 are withheld genuine complete historical printer payloads. Both models examine 6 whole-packet byte/word presentations and appropriate word endians.

## Model A: subtract-with-carry / lagged generator, complete search

Search widths `w ∈ {8,16,24,32,48,64}` with consecutively reassembled `w`-bit words (including words crossing 16-byte packet boundaries). For every lag `2≤r≤64, 1≤s<r`, both orientations of the difference, permit an *independently free* borrow of 0 or 1 at every recurrence step. Require every training word after lag `r` to satisfy `x[n] = ±(x[n-s]-x[n-r])-borrow (mod 2^w)`. Allowing a free borrow is an optimistic **superset** of a genuine coherent SWC generator, so nonfit excludes each exact serialized continuous-stream producer.

**290,304** producer/layout/lag assignments; **0** whole-training survivors and hence **0** entire withheld 32-packet predictions. The longest initial compatible stretch after lag was only **two words**. Independently planted, actual borrow-propagating 24bit lag24/lag10 streams regenerated the withheld 32 synthetic packets and were correctly detected; synthetic exact fit count was one. No selected K04 candidate generated.

## Model B: WELL512a state recovery, complete training mismatch

Implement the **errata-corrected** 512-bit GF(2) WELL512a transition from the [Apache Commons RNG implementation](https://commons.apache.org/proper/commons-rng/commons-rng-core/jacoco/org.apache.commons.rng.core.source32/Well512a.java.html). Initialize 16 arbitrary unknown 32-bit state words with 512 unit GF(2) variables. Propagate symbolic bit vectors through outputs, solve the first 16 complete observed outputs by GF(2) Gaussian elimination, and test the next output and onward without refitting. Original packets are split into four 32bit words under each of six whole-packet views and both byte endians (12 complete presentations). The cyclic state-index rotation is absorbed in the arbitrary 16-word initial state.

For **all 12 original presentation choices**, 16 observed outputs give **rank 512**, then **output 17** introduces a contradictory complete source equation. Thus **0** original source-compatible continuous WELL512a streams and **0** actual 32-packet holdout predictions. Positive control: an independently generated 512bit WELL512a state is recovered at rank512 and predicts **all 128 heldout 32bit words (32 whole packets)** exactly.

## Interpretation and next allocation

These are producer-model exclusions under the stated continuous raw-byte serialization, not printer attribution. The SWC model excludes coherent borrows at every tested original lag if its outputs were emitted continuously under tested widths/views; the WELL512a model excludes native consecutive 32bit outputs under tested views. Hidden per-job draws, re-seeding, arbitrary output skips, different engines, queue/physical-copy corrections, and source-authenticated selector stages remain open. Neither model had any evidence that it was historically used, and neither should be expanded into adjacent brute-force grids without such evidence.

The untouched REC8/1 verifier remains K01/K02/K03/K05/K06/K07 PASS, K04/K08 unresolved and combined INCOMPLETE. No official source, routing, acceptance, verifier or candidate was modified.

Source-only local executable SFTs from this incarnation: `k04_swc_lagged_source_sft.py` and `k04_well512a_source_inversion_sft.py` (retained as reproducible scripts in this invocation's delivered local research artifacts).