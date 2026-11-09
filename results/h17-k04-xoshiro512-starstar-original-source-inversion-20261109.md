# K04: exact source-first 512-bit xoshiro512** state inversion

**Agent 19 | 9 November 2026 | Original-source producer exclusion, no REC8 acceptance**

## Recovery hypothesis and executable discriminator

A different potential K04 selected-object producer is the published Blackman–Vigna **xoshiro512\*\*** state machine. It has eight 64-bit state words, a nonlinear-looking output transform but a reversible 64-bit output function and a GF(2)-linear internal state transition. If archived 16-byte printer payloads were pairs of native 64-bit xoshiro512** outputs from one continuing state, eight native outputs would constrain all 512 state bits, and remaining whole historical packets would validate or falsify the model without touching the disputed selected ESC-N ACK2 bytes. A genuine successful same-source model would predict the selected job only after its gap/selection rule was established.

Specifically, native output `rotl(s[1]*5 mod 2^64,7)*9 mod 2^64` inverts to `rotr(output*9^-1 mod 2^64,7)*5^-1 mod 2^64`. Every inferred pre-output `s[1]` bit is a linear equation in the eight unknown original 64-bit words. Gaussian elimination recovers the full native state on a planted 512-bit original, then predicts unseen outputs. This is a source-producing algorithm test, **not** another Hamming correction of ACK2 or assumed CPython MT p951 chronology.

## Frozen source and original test

- Original `resources/evidence/print/spool-reconstruction.log`, SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`.
- Exactly 128 intact ordinary first-attempt job packets `PS-261003-0300..0427` were parsed for this test; selected attempt 2 at job `0417` excluded.
- Four source views: two byte orders within each 64-bit half and two eight-byte half orders.
- **127** constant native-output interpacket strides 2 through 128; the two within-packet outputs use adjacent native stages.
- **729** distinct class-driven per-job variable-gap schedules for `LABEL/STORES/RECOVER`, with costs 0..8.
- **648** additional distinct destination-driven schedules for `store/bench/desk`, costs 0..8, after duplicate stage geometries are removed.
- **12** additional unique schedules with binary additive class+destination costs.
- In total **1,516 distinct native-stage schedules**, times four original 64-bit serializers = **6,064 complete source-only producer assignments**.

For each assignment, recover the state algebraically from the first up to 16 native output observations. If these observations are inconsistent, the model fails without a selected-target hash probe. The entire authentic 256-word stream is reserved as a full-object holdout if an assignment survives.

**Original-source result: zero source-consistent assignments.** Every model produces an exact linear contradiction within its 16-word training window; none reaches the target and none is used to claim K04 bytes. A separate fixed-stride screen verified contradictions across all 127 interpacket strides before output 16 as well.

## Controls, trace and interpretation

On synthetically generated native xoshiro512** states with fully withheld future outputs, the same inverse reconstructs the **exact 512-bit state**, including native per-job strides 2, 3, 17, 64 and 128 and a nonuniform source-role schedule, all at rank 512. Each source model then predicts 240 independent further 64-bit outputs exactly. Deliberately changing one observed output bit fails recovery of the planted state or produces contradiction. These planted positives establish the exact 512-bit inverse works on valid data.

[Source-pinned single-file Python reproducer](../agents/agent19/k04_xoshiro512_state_inverse_sft.py), committed at `56c64afd631677648c2a4dbc425c51b75a1c8fa8`. It uses only the Python standard library and original `resources/` input. The executed local source-equivalent tests are `agent19_xoshiro512_starstar_sft.py`, `agent19_xoshiro512_stride_probe.py`, and `agent19_xoshiro512_metadata_stride_probe.py`.

**Scope:** this excludes the exact shared-state xoshiro512** emitter with two full native 64-bit output words per packet and the enumerated constant or metadata-dependent gaps. It does not exclude alternate output mixers (xoshiro512+, ++), halfwords of separate native outputs, timestamp reseeding, discarded outputs outside the defined schedules, independent physical copy corruption, or any other source-to-selected-object mechanism. No authentic physical K04 selected bit was recovered, no K08 final wording discovered, and six accepted components plus combined INCOMPLETE remain unchanged.

**Next discriminator:** any alternative output mixer/producer needs to predict unseen complete real printer packets, preferably with a same-role selected-attempt/copy distinction, before spending compute predicting physical K04.
