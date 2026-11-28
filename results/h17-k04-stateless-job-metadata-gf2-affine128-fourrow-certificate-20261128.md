# K04: stateless job-metadata affine 128-bit issuer, four-record original contradiction

**Agent 39 | 28 November 2026 | complete candidate and independently held-out original packets | no K04 component recovered**

## A source-selected and parameter-complete alternative to random-stream issuers

The original 128 ordinary printer jobs each retain an exact job suffix, `CLASS`, `DEST` and a complete 16-byte opaque ACK payload. An alternate printer could deterministically issue that packet from routing metadata, with no persistent PRNG state at all. Rather than guess a hash function, exhaust **the entire family of GF(2)-affine maps** from a fixed source-derived input encoding to the full **128-bit packet**:

```text
Y = M * (1 || job_suffix_encoding || onehot(CLASS) || onehot(DEST))
```

where `M` is an arbitrary binary matrix and there are **no constraints whatsoever on its 128 output rows**. The leading one permits a constant affine offset. Freeze both legitimate representations of the observed four-digit job suffix: numeric integer bits, and original four ASCII decimal digits. Freeze the three actual class and three destination values as categorical one-hot bits. This family contains every XOR linear secret-key/constant combination on those exact fields, not merely seeded examples.

An exact GF(2) basis of original source metadata inputs determines each output on the span of the observed inputs without selecting free coefficients. The earliest linearly independent ordinary ACKs fix the basis; every remaining complete intact 16-byte ordinary packet is an independent full-output test. The selected `PS-261003-0417`, `RECOVER`, `bench`, 18:02 attempt-2 ACK **copied payload is never read or fitted**. The intact source metadata alone yields one *complete hypothetical* physical coupon in each of the two input encodings. Apply the original ESC-N 16-byte XOR mask and the entire unchanged K04 SHA256 commitment. Two separately retained later printer ACKs, including another attempt-2 ACK, are independent whole-packet class/stage holdouts.

No source says the original writer used an affine metadata issuer, so this is a bounded, falsifiable alternative to the already-tested stochastic native generators, not a printer authenticity claim.

## Four-row mathematical impossibility certificate — independent of K04 target

A GF(2)-linear map cannot change a zero XOR of source inputs into a nonzero XOR of their outputs. In particular the *four untouched original ordinary rows* with zero-based indices **0, 3, 5, 6** have these exact source fields:

| Index | Job | CLASS | DEST |
| ---: | --- | --- | --- |
| 0 | PS-261003-0300 | LABEL | store |
| 3 | PS-261003-0303 | RECOVER | desk |
| 5 | PS-261003-0305 | LABEL | store |
| 6 | PS-261003-0306 | RECOVER | desk |

For numeric job suffixes, `300 XOR 303 XOR 305 XOR 306 = 0`. For each ASCII digit of the same four job suffixes, the bytewise XOR likewise vanishes. The affine leading ones cancel four times; each one-hot class/destination category occurs exactly twice. Therefore the **complete augmented input XOR is zero in both source encodings**.

The four original 128-bit printer ACK payloads instead have **55 nonzero bits in their XOR**. This is an exact, original-source **four-row counterexample against every possible binary or ASCII GF(2)-affine metadata-to-payload map in the defined family**. It requires neither the selected 18:02 copied ACK2, the route mask nor the original K04 target hash. There is no need for a seed dictionary or a larger coefficient sweep to refute these precise global issuer models.

The source-pinned reproducer asserts the zero source XOR and exactly 55 discrepant payload bits for both encodings. It additionally creates independent arbitrary random affine maps over the same source features and verifies that the program recovers all whole 128-bit planted outputs and their route-mask/full-hash selected-coupon controls in **2/2 synthetic source-fit cases**.

## Source-frozen whole-object results

| Source metadata representation | Original independent source input rank | Whole intact ordinary printer holdouts | Exact 16-byte packet matches | Separate intact later printer ACK holdouts | Complete hypothetical K04 checks | Accepted K04 |
| --- | ---: | ---: | ---: | --- | ---: | ---: |
| Numeric four-digit job suffix + categorical CLASS/DEST | **13** | **115** | **0** | **0/2** | **1** | **0** |
| Literal four-ASCII-digit suffix + categorical CLASS/DEST | **14** | **114** | **0** | **0/2** | **1** | **0** |
| **Total model tests** | | **229** | **0** | **0/4** | **2** | **0** |

The two intact later ACKs are the preserved unrelated special printer jobs after the selected 18:02 event. They are withheld from all map fitting and checked at the same **whole 128-bit packet** width. They do not establish that the selected physical paper was issued by any fitted model.

Each model's source mapping is internally contradictory. The 4-row certificate above is a smaller decisive witness; the 229 source holdouts and the independently retained later ACKs provide redundant, role-relevant historical falsifiers. The two fully reconstructed conditional coupons still fail the unchanged original complete K04 commitment when routed through the original mask.

## Exact scope and next move

The result closes **both fixed GF(2)-affine metadata-to-whole-packet generators for the named numeric/ASCII job representations and given categorical one-hots**. It does not exclude SHA/HMAC keyed issuance, nonlinear carries, actual per-packet random states, different metadata fields or stages, adaptive class-specific coefficient maps, hidden native queue contents, or an original physical coupon whose bytes never entered the log. The copied ACK2's dispatch status cannot fill that gap.

All source pins, the canonical candidate, original route, commitment and verifier remain unchanged. No K08 author-final wording was recovered. **K01, K02, K03, K05, K06 and K07 remain PASS; K04 and K08 remain MISSING; REC8/1 combined remains INCOMPLETE.**

**Reproducer:** [exact 128-bit metadata-affine and four-source-record certificate](../agents/agent39/k04_stateless_metadata_affine128_sft.py), from repo root: `python agents/agent39/k04_stateless_metadata_affine128_sft.py --root resources`. The original source is hash-gated to `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`, and output reports only ranks, full-packet acceptance counts and source contradiction counts. No original candidate value is printed or sent to CI.
