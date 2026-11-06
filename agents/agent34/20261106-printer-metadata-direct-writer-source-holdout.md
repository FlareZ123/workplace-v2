# K04: direct packet-output CLASS/DEST issuer, original-source train/heldout test (6 Nov 2026)

**Agent34, source-only pilot.** Original six REC8 components PASS, K04/K08 missing; no K04 candidate constructed. This tests a causal *same/adjacent intact-packet* metadata writer, rather than Ag25's next-stage q+4 high-bit rule. It was executed against the original unchanged attached ZIP.

## Frozen output hypothesis

Read original `resources/evidence/print/spool-reconstruction.log`, SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. Parse 133 complete source packets, but **fit using routine rows0..127 only**; selected disputed row129 is never fitted and no K04 acceptance digest is consulted.

For each routine row i, predict its DEST (store,desk,bench) or CLASS (LABEL,STORES,RECOVER) using exactly one 32-bit source word from packet i-1, i, or i+1. For each source-relative position, test both little/big endian, both raw and standard MT19937 inverse-tempered representations, each of four 32bit lanes, then one of 34 digitizers:
- `(word>>shift)&3`, shift0..30: codes0..2 accepted, code3 excluded as a rejected draw;
- `word%3`, `(word&65535)%3`, `(word>>16)%3`: code always0..2.

That makes **1,632 candidate source features**, each with all six fixed code-to-category permutations. Fit score on first **64 original routine rows only**: `correct - covered/3`, rank by score, evaluate the five best unchanged against the **separate heldout rows64..127**. The class and destination tests independently use the same family; the scored category mappings are allowed to differ. No target-specific parameters are chosen.

## Result

**DEST best training model:** same packet, little endian, MT-native (inverse temper), word0 bit9..10, mapping code0=desk /1=store /2=bench. Training **30/49** source-fixed rows; heldout **19/55** (uniform-label expectation18.33). Independent actual-label most-frequent baseline **16/55**. No material source-only predictive lift.

**DEST second-best training model:** *previous* packet, little endian, MT-native word0 `%3`, mapping code0=desk /1=store /2=bench. Training **32/63**, heldout **27/64**, baseline19/64. Overall **59/127** correct. A separate read-only 100,000-run label shuffle within each original CLASS, preserving class membership and destination frequencies, yielded fixed-model full-sample tail **p≈0.00108**, but prospective heldout-only tail **p≈0.08209**. The post-hoc full-sample p is **not** adjusted for 1,632 feature searches, so it cannot certify a true issuer.

**CLASS best training model:** following packet, little endian, native word3 high bits23..24, code0=RECOVER/1=LABEL/2=STORES. Training **33/54**, heldout only **11/44** (uniform expectation14.67), demonstrating the danger of training-only matches. The next two CLASS features achieve **20/52** heldout against expectation17.33.

The selected row was inspected only after these prospective tests: under the second-best DEST model, the next row130's `bench` destination would demand a different modulo-3 class than the **copied** q951 output, but that rule misses **68/127** intact originals, so this mismatch is not evidence of selected physical damage or an authentic recovered bit.

Positive planted control: assign destination labels in ordinary rows according to a real member of the exact feature family (previous packet native word0 2-bit digitizer); training selection achieves **48/48** covered heldout predictions. All candidate rules, training split, source records and acceptance labels are otherwise untouched.

## Decision

No specified direct-packet two-bit/remainder issuer generalizes sufficiently to provide a usable selected physical-coupon discriminator. Ag25's conditional q+4 association should not be silently promoted to a deterministic metadata writer. A new mechanism must predict heldout **whole selected-source values** more strongly than these category correlations. This note closes exactly this source-aligned single-word feature class, not arbitrary nonlinear metadata/capture transformations, other emitters, or the final K08 literal search.

Original verifier, route mask, acceptance and canonical candidate unchanged. Source K04 authenticated bits remain 0, K08 author-final words 0.
