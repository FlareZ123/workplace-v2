# K04 intact-printer source-predictor experiment

**Agent 4, 3 November 2026.** Input is the original printer spool with SHA-256 7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083. The selected disputed 18:02 ACK and K04 commitment were excluded from model construction.

## Full-coupon producer hypotheses

**Metadata XOR family.** For 63 source-field serializations and six unsalted 16-byte digest reductions, infer a single fixed unknown XOR offset from the first original ACK and predict the remaining intact records. All 378 models fail on the next copied ACK in every tested stratum: all other ACKs (130), RECOVER ACKs (37), RECOVER ACKs to bench (12), and all ACKs to bench (46). A synthetic two-record positive passes.

**Arbitrary affine 32/64-bit word recurrence.** Unlike fitting a named generator, learn any time-invariant GF(2)-linear-plus-constant mapping from complete prior words. Across 128 intact chronological pre-retry ACK packets, all 24 permutations of 32-bit word order contradict at outputs 30–32 (one lag), 59–67 (two lags), and 128–133 (four lags). Both 64-bit word orders contradict at output 65 (one lag) or 131 (two lags). A planted xorshift-plus-constant generator passes. An unrestricted 128-bit packet-state recurrence has only 127 pre-retry transitions against 129 affine features and is explicitly underdetermined.

These are original-source model failures. Unknown producer state, skipped draws, nonlinear transforms, stage changes and physical-versus-copy differences are outside the tested assumptions. Neither selected K04 bits nor final K08 words were recovered. Six original components remain accepted, combined recovery INCOMPLETE.

Reproducer: [Agent 4 source-predictor SFT](../agents/agent4/k04_source_predictor_sft.py). Original evidence and acceptance files unchanged.
