# H-17 K04: complete one-to-five bit faults in a 624-word MT register, stage951

**Agent 3 | 10 November 2026 | Original K04 SHA256: zero accepted values.**

## Source-to-target hypothesis

The selected ESC-N RECOVER ACK attempt 2 (3 October 2026 18:02 UTC, PS-261003-0417) has a **copied** 16byte payload, A9A9DC5731A5E2AE879C47215C2559D5, that does not pass the original K04 route-masked acceptance commitment. This experiment tests a *different stage of a native MT19937 writer/copy fault*: the copied and original coupon might have diverged because one-to-five bits in a **624x32-bit earlier native state register** differ, a full 951 native draws before the selected fourword output.

This model is **unproven historical software and fault behavior**. The printer/recorder's source-only p951 MT stage layout is itself conditional. An upstream generator fault in a persistent shared printer stream would also alter other earlier ordinary outputs; the model is most plausible for a selected-stage replay or independent copied-buffer emitter. It does not establish either.

Original source spool SHA256: 7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083.

Original K04 route mask: 8556C8CB6140A7F9A5123AC7571BEE1C.

Original immutable K04 SHA256 commitment: 930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0.

The original copied 16-byte payload, job selector, mask and commitment are all asserted. The original archive, canonical candidate, route and verifier are never edited.

## Exact 19,968-bit influence map

Initialize an all-zero native 624-word register and flip each one of its 19,968 physical bits separately. Propagate with the standard native MT19937 recurrence:

    X[t+624] = X[t+397] XOR (((X[t].MSB | X[t+1].low31)>>1)
                          XOR (0x9908B0DF if X[t+1].lowbit else 0))

Then extract complete native words X[951..954] and classify their 128bit error signature before MT tempering. Because the transition and tempering are GF(2)-linear, any multi-bit initial-register error is the XOR sum of its single-bit effects. The complete original source-independent influence map contains:

| Influence category | Distinct effect signatures |
|---|---:|
| Physically nonzero single-register-bit influences (including duplicate effects) | 384 |
| Distinct one-native-bit effects on the four target words | 128 |
| Distinct **15-native-bit feedback polynomial effects**, one per target word | 4 |
| **All distinct nonzero output effects from a single upstream bit** | **132** |

The other 19,584 individual initial-register bits have zero effect on this particular fourword target window at the exact stage. The 384 active physical bits collapse to 132 possible output signatures because several upstream bits have the same effect.

This exposes a distinct correction family. One **single** upstream state-register bit can trigger the 15-bit MT feedback constant 0x9908B0DF in the target native word, exceeding the five-native-bit coupon fault bound already completed by Agent3. A bounded source-defined exhaustive search is therefore feasible by enumerating the **132 unique influence columns** rather than the massive 19,968-bit physical fault combinations.

## Exhaustive complete original K04 test

Enumerate every selection of up to five distinct nonzero influence columns, including at least one of the four 15bit feedback columns. Selections involving only the 128 onebit columns were already exhausted in the separate five-native-bit study ([prior experiment](h17-k04-native-mt-temper-fivebit-fault-20261110.md)). Duplicate or cancelling actual physical faults reduce to one of these lower-cardinality unique signatures and are also covered. Each subset yields a complete candidate native fourword delta, exactly tempered, XORed into the copied 16byte coupon, route-masked, and compared with all 256 bits of the original SHA256 commitment.

The complete new domain is the exact sum, for fault weight 1 through 5, of C(132,k)-C(128,k) = **46,201,487 distinct effect-column selections**. This family has unique coupon effects: each 15bit feedback vector requires at least eleven separate onebit changes to cancel when total selected columns are at most five. The source-only alternative eight-output-bit shell is re-used for **32** cases whose actual tempered coupon XOR has Hamming distance at most eight, and these cases are not redundantly hashed.

| Original full-coupon checks | Exact result |
| --- | ---: |
| Complete upstream effect-column combinations with one or more feedback columns | **46,201,487** |
| Already checked in complete output Hamming-distance <=8 shell | **32** |
| **Additional complete original K04 SHA256 checks** | **46,201,455** |
| Original accepted K04 components | **0** |
| Independently planted synthetic complete-component positives | **1** |

Execution used the unchanged original local ZIP's spool file. The C++20/OpenSSL source computes **all 19,968 one-hot original-state effects independently** rather than assuming the 132-column form, and checks the 384 active/132 distinct/native-singlebit/feedback counts before candidate hashing. It asserts the exact original source digest, selected job identity, copied payload, route mask and untouched K04 target. The run completed in approximately 14 seconds on the local machine.

The synthetic full-coupon positive is created from one *real* one-bit upstream feedback influence at native selected word0 plus four different one-native-bit upstream influences at native coupon bit positions 0,17,34,67. The synthetic coupon is passed through the true MT temper, unchanged route mask and full SHA256. The exact complete synthetic component is recovered once in the same enumerator (no synthetic target is substituted for the authentic SHA target).

Reproducer: [Agent3 stage951 upstream MT register fault SFT](../agents/agent3/k04_mt_ancestor_register_fivebit_sft.cpp). C++20 with OpenSSL libcrypto; execute with the source spool log path. All source SHA assertions, full target comparison, complete domain count and planted-positive count must pass.

## Interpretation

**This new bounded, source-geometry-defined class fails to recover K04.** It excludes the hypothesis of at most five initial MT-register-bit differences between the two selected-event coupon emitters under the exact native stage951 and output serializer model, including defects that expand into 15 native target bits through MT feedback. It is distinct from the prior <=5 native target-bit error search and from prior raw output-Hamming-shell exhaustion.

The absent physical selected-coupon integrity witness remains unresolved, and the K08 exact final author wording remains unquoted. No authentic K04 selected bit or K08 final word has been newly recovered. Six original REC8/1 components remain individually PASS and combined acceptance INCOMPLETE.

A productive next attack should change the selected-stage origin, the emitter/copy relationship or the author-final version source. Broadening to six register faults would be another large model-conditioned search without increased historical evidence.
