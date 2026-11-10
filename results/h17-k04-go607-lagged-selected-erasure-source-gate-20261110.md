# H-17 K04: Go 607/273 lagged-additive source and selected erasure test

**Agent 40, 10 November 2026.** The selected K04 coupon remains unresolved; original REC8/1 status is six individual PASS, K04 and K08 missing, combined INCOMPLETE.

## A new complete coupon mechanism

Go's legacy `math/rand` source has a 607-word 64-bit lagged-additive internal register, in which subsequent generator words have the form `X[n]=(X[n-607]+X[n-273]) mod 2^64`. Under either low-32 or high-32 views, and the usual `Uint32` view using bits31..62, 32-bit observations `q` satisfy a useful necessary carry condition:

`(q[n]-q[n-607]-q[n-273]) mod 2^32` belongs to `{0,1}`.

The supplied archive has 133 four-word printer packets, one of which is the disputed historically selected 18:02 ACK2. Its remaining 132 packets provide 528 known words. The TRP2 dump has 88 recorded 32-bit control fields, while authenticated K01 and K06 together provide eight additional 32-bit words. With the selected printer packet *withheld* as four erasures, those cohorts occupy **628 positions** including the four unknown words. For block orderings placing the erased packet in the last 21 outputs, the Go recurrence could derive **two candidate values per selected 32-bit word**, yielding **16 complete coupon candidates** per source-compatible layout, with the original K04 masked-component XOR and full 256-bit SHA256 acceptance to select the genuine coupon.

This construction is deliberately different from concatenating 624 known source words and *generating the next* MT19937 output packet. It predicts the actual selected packet **in place** from two lagged source predecessors. The evidence does not attest that the printer uses Go, that its 32-bit source encoding matches this model, or that printer, recorder and accepted text-derived bytes come from a shared generator.

## Completed original-source gate

Read-only [one-file reproducer](../agents/agent40/k04_go607_628_erasure_sft.py) pins the original 132-packet spool SHA256 and recorder SHA256. It suppresses the entire selected 16-byte ACK2, tests all six whole-group orders, three independent 32-bit byte orientations and forward/reverse group orderings. It retains layouts only when all four selected words lie in the recurrence-predictable suffix; all other printer words and source groups remain genuine original observations.

- **128** eligible, distinct source-layout assignments were evaluated.
- **0** assignments satisfy the necessary complete-source additive recurrence.
- Therefore **0** historically eligible full coupons were passed to the K04 acceptance check, and **0** K04 values were recovered. This is a *source gate failure*, not a negative from guessing target bytes.
- **3/3 planted controls passed**: low32, Go-like bits31..62 and high32 views of an independently generated genuine 64-bit lagged-additive stream, with the selected four positions removed and exactly recovered within their two-valued domains.

The original K04 XOR mask and full-SHA256 commitment were read for the legitimate whole-coupon acceptance stage, and neither the suspect selected packet's bytes nor any acceptance target altered the source-selection test. All original records, canonical candidate and official verifier remain unchanged. 

## What the failure teaches

The exact 628-position source-count geometry creates a useful *target-identifying erasure mechanism* if a comparable historical lagged source is found, but the retained H-17 source words reject this specific Go 607/273 cross-cohort placement before the target is considered. Do not infer an authentic printer PRNG from matching number counts. Further work needs an observable producer-stage relation that predicts an independent complete printer payload, or a physical selected-copy witness. The final author-selected K08 wording is a separate unresolved problem.
