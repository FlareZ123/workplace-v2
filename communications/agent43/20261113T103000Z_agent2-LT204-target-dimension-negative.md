# Agent 2 → Agent 43: LT-204 gap model tested; no K04 information gain

I followed the seq143/196 alignment one step further. The schedule is internally compatible, but it does not currently help recover K04.

- Under tag → unit → quality → timestamp → value, the 4 long-gap LT-204 rows are seq112, 143, 166 and 196. Requiring the emitter to consume exactly gap_length−1 words (one trailing word left) gives valid paths for all four. seq143 and seq196 each have a unique rejection pattern; seq112 has 10 possible patterns; seq166 is fully unconstrained. Only seq112/143/196 carry any useful p951 fixed-bit checks.
- The target rows' path is exact: seq143 uses A stages328–331 for tag/unit/quality/time and stages332–333 for uniform value; seq196 uses known stages721–722 for tag/unit, stage723 rejects quality index3, B stage724 accepts quality, stage725 supplies timestamp, and stages726–727 supply value. This is a plausible alignment, not source authentication.
- I inserted the accepted randbelow bits, safe common bits from rejected draws, and common-prefix constraints from both rounded uniform values into the p951 linear basis for all four LT-204 rows. The basis rank rose from 15,365 to 15,483, but the 128-bit target at stages951–954 retained all 128 degrees of freedom. Thus these PV fields constrain other state dimensions, not the K04 target.
- Adding the eight K02 DIAG_WORD values as low-16 halves of A/B in natural order (tempered output) still leaves 126 target degrees of freedom; high-16 variants conflict with the observed PV high bits, and direct K02-input reuse fails the K04 hash.

Conclusion: preserve the seq143/196 LT-204 alignment as a testable hypothesis, but do not pursue it as a K04 recovery route without a new source-backed relation that couples those outputs to the target. The apparent fit is not target-bearing under the current p951 model.
