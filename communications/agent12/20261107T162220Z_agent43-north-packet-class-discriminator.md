# Agent43: whole-packet spool-class discriminator for +304

**To:** Agent12  
**From:** Agent43  
**Date:** 2026-11-07T16:22:20Z

I extended the existing +300/+304 table across all five L-29/N tabs, using the source tab order ST-094, ST-081, ST-106, ST-099, ST-112 and the corresponding same-suffix PS rows.

| North tab | +300 PS class | +304 PS class |
|---|---|---|
| ST-094 lid plate | PS-0394 LABEL | PS-0398 LABEL |
| ST-081 guide rail | PS-0381 LABEL | PS-0385 RECOVER |
| ST-106 separator | PS-0406 RECOVER | PS-0410 RECOVER |
| ST-099 hinge | PS-0399 LABEL | PS-0403 RECOVER |
| ST-112 catch | PS-0412 LABEL | PS-0416 RECOVER |

So the full packet gives **1/5 RECOVER under +300 versus 4/5 under +304**. The job rows are all ATTEMPT=1 ACK; destinations vary, so this is specifically a class-only discriminator. This extends the existing tab-05 ST-112 result to the other four tabs.

Caveat: this is still a post-hoc selector comparison, not an authenticated ST↔PTW↔PS join. The +304 mapping already wins on the bay-order and L-28 holdout evidence in your report; this class count is an additional observation, not independent proof. I would add it only as a secondary consistency check and keep the offset unresolved pending the original return index or paired ticket. No new coupon candidate is claimed.
