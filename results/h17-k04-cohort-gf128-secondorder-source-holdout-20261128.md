# K04: class/destination-local GF(2^128) order-two producer, original whole-packet holdout rejection

**Agent 39 | 28 November 2026 | source-specific independent coupon reconstruction | no recovered K04**

## Question and frozen producer

The selected printer record is the original `PS-261003-0417` `RECOVER/bench` attempt-2 ACK, whose copied 16-byte payload is **not authenticated** as a physical coupon. Instead of treating all ordinary print rows as one random stream or fitting the disputed ACK copy, this experiment tests whether the printer maintained an **independent second-order 128-bit finite-field state stream per original CLASS, DEST or CLASS×DEST** routing category.

The proposed source-aligned recurrence for a category's successive 16-byte packets is

```text
X[n+2] = a*X[n+1] XOR b*X[n]  over GF(2^128)
```

where multiplication reduces modulo `x^128+x^7+x^2+x+1`. Each category has an arbitrary, separately learned coefficient pair `(a,b)` and first two words. No shared state across categories and no per-category seed dictionary are assumed. Neither this producer nor its field polynomial is **historically attested**; the model is an explicitly testable source-conditioned hypothesis, not a recovered original printer implementation.

For each category, **only its first four** preserved ordinary ACK packets train the exact algebraic coefficients. The remaining original packets for that category are complete 128-bit holdouts, predicted using the two preceding *real* original packets for each one-step comparison (not propagated incorrect predictions). The category selected by the original 18:01 `RECOVER/bench` request supplies the candidate physical 18:02 coupon: apply its learned recurrence to the last preceding category-specific ordinary packet and the exact intact 18:01 REQUESTED1 payload. The 18:03 REQUESTED3 packet is an independent same-job 128-bit holdout.

**Never fit or read the disputed copied ACK2 PAYLOAD.** Form each complete hypothetical coupon, apply the unaltered original K04 route XOR mask, and check the full original SHA256 K04 commitment **before** considering whether an original holdout matched. Four native 16-byte layouts are predeclared: original/reversed order of four 32-bit words × original/reversed bytes within each word. Three category selectors × four layouts = **12 complete coupon producer models**.

## Exact solvability

For four authentic consecutive source values `x0,x1,x2,x3`, the field determinant is `D=x1*x1 XOR x0*x2`. If `D != 0`, the coefficients are uniquely determined:

```text
a = (x2*x1 XOR x3*x0) / D
b = (x3*x1 XOR x2*x2) / D
```

using exact GF(2^128) inverses. All original trained groups are nonsingular under each predeclared layout. Fitted equations are replayed exactly. There is no hidden brute-force seed, missing coefficient bit or discarded SAT model.

Independent seeded synthetic streams with arbitrary per-category 128-bit coefficients and states correctly recover `(a,b)` and reproduce all their withheld full packets under all 12 model combinations; **12/12 synthetic source/holdout controls PASS**. Sixteen independently generated nonzero field elements also pass `x*inverse(x)=1`.

## Original execution

Original printer `resources/evidence/print/spool-reconstruction.log` SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083` was checked before use. Exactly 128 ordinary entries are classified. The last three selected-job records preserve the exact 18:01/18:02/18:03 identities and are excluded from training. Only 18:01 and 18:03 intact contents enter the candidate/holdout path.

| Source category scheme | Streams per model | Original intact heldout packet checks over four serializers | Exact 128-bit matches | K04 whole-component commitment matches |
| --- | ---: | ---: | ---: | ---: |
| CLASS | 3 | 464 | 0 | 0/4 |
| DEST | 3 | 464 | 0 | 0/4 |
| CLASS×DEST | 9 | 368 | 0 | 0/4 |
| **Total** | **15 category streams per serializer** | **1,296** | **0** | **0/12** |

Every source-complete original packet prediction disagrees in multiple bytes. The exact selected job's **18:01 REQUESTED1 also fails the corresponding one-step cohort forecast in 12/12 models**, with 55–71 disagreeing bits. All twelve independently reconstructed 18:02 coupon values fail the unchanged original commitment, and their 18:03 REQUESTED3 predictions disagree by 52–70 bits in all twelve layouts. The 18:03 holdout is not used as a veto before testing K04 acceptance.

No original source file, physical coupon, canonical candidate, route, acceptance, or verifier was edited; original-sourced candidate bytes and field coefficients are not published or run through public CI.

## Distinction from predecessors and decision

The earlier exact global xoshiro/xorshift and GF(256) recurrence tests assumed a single writer across ordinary rows; Agent39's same-day multiplexed xoshiro128** screen instead used a **GF(2)-linear four-output state machine** per class/destination stream; earlier GF(2^128) affine and ring-affine retry inversions used **first-order same-job/cross-job transitions**, not the present independently trained second-order category-specific publisher. This is a new complete-object reconstruction with both independent ordinary-cohort and same-job 128-bit holdouts.

The result **rejects only no-reset, one-step second-order GF(2^128) category streams and the precise selected-coupon source placement under those groups and layouts**. It does not exclude a different polynomial, nonlinear/keyed state machine, per-request reset, variable skips, alternate physical copy-stage, or the unobserved original paper. Since the model fails independent original controls and original K04 commitment, its generated coupon cannot be treated as authentic.

**Recovery remains six original component PASS, K04/K08 MISSING and combined REC8/1 INCOMPLETE.** Do not broaden this into arbitrary finite-field model families without an original firmware/schema or recovered physical-media witness.

Reproducer: [portable source-pinned original/synthetic test](../agents/agent39/k04_cohort_gf128_secondorder_sft.py). Invoke `python agents/agent39/k04_cohort_gf128_secondorder_sft.py --root resources` from the repo root. It prints only aggregate original-model whole-packet error counts, synthetic controls and complete original commitment hit flags.
