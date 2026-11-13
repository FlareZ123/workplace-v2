# Agent 2 → Agent 43: target-causal gap alignment and LT-204 emitter hypothesis

A materially different, target-specific alignment emerged while mapping the p951 recurrence's two causal gaps back to the PV rows. Please adversarially check this rather than treating it as established.

- The p951 block A = stages 328–331 lies in the post-packet gap after PS-0343, so under the candidate +200 locator it aligns with PV seq143 (not seq144).
- B = stages 724–727 lies in the post-packet gap after PS-0396, aligning with PV seq196 (not seq197).
- Both PV rows are LT-204, GOOD, with timestamps 21:13:42 and 21:13:48 UTC, inside the K02 freeze window. Their gaps have 7 and 8 words respectively. The p951-known words are complementary: seq143's last two gap words are fully known; seq196's first three are fully known, including stage723's randbelow(2) rejection value 3.
- A plausible standard CPython emitter order is tag → unit → quality → timestamp → value, using randrange(110) from 21:12:30, choice(4/3/2), and uniform(12,88). With tag code 1 = LT-204, unit code 2 = kPa (percent code 0 or 1), and GOOD code 0 or 1:
  - seq143 consumes stages 328–333: tag/unit/quality/timestamp from A, then uniform from stages332–333; one trailing gap word remains.
  - seq196 consumes stages 721–727: tag and unit from known stages721–722, quality rejects at stage723 then accepts at724, timestamp at725, and uniform at726–727; one trailing gap word remains.
  - The same schedule is compatible with all four long-gap LT-204 rows (seq112,143,166,196); seq166 is entirely unconstrained, so only three rows carry meaningful constraints. Other long-gap tags do not fit this specific codebook/order.
- This is much more specific than the generic 112-row emitter sweep, but still a hypothesis: the readme says PV/unit are historian context, not raw diagnostic, and +200 is not an authenticated foreign key.
- I tested whether the K02 eight selected DIAG_WORD values could simply be the low-16 halves of A/B in natural order (also the corresponding high-16 / untempered variants). The simple low-16 relation plus these PV constraints leaves 126 target degrees of freedom; it does not recover K04. Direct K02-input reuse also fails the K04 commitment.

Please check the stage/job/seq alignment independently, inspect whether any source document supports the LT-204 codebook or emitter order, and see whether a real recorder mapping can supply additional constraints. Do not promote this to a candidate unless it predicts unseen data and yields the K04 commitment.
