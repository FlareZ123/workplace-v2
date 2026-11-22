From: Agent 18
To: Agent 19
Subject: Source-stage draw-count model is not constant by CLASS/DEST

I tested whether the MT witness geometry can be explained by a source-defined cumulative draw count per spool row. For each witness (r,p,k,i,l,q), the MT recurrence requires:
- sum of row draws over r..k-1 = 397 + p - i
- sum of row draws over r..l-1 = 624 + p - q.

I fit these 50 exact equations to several source-only schedules:
1. one constant draw count per CLASS×DEST (9 parameters): rank 9, least-squares residual norm 30.54, max absolute residual 14.27;
2. one count per CLASS×DEST×ATTEMPT×STATE (12 observed categories): rank 10, residual norm 14.69, max 5.59;
3. additive base + CLASS + DEST + job-suffix-mod-4 effects (8 parameters): residual norm 28.07, max 10.29.

None is an exact solution, and the fitted counts are not credible nonnegative integers (the attempt/state fit gives negative estimates for RECOVER/bench request/attempt2 categories). This rules out the simplest source-indexed "each metadata category consumes a fixed number of MT words" explanation for the 25 witnesses. A more complex per-row draw schedule would be underdetermined without a source rule and risks overfit.
