# Independent Agent47 check: PS-0417 target-row MT witnesses

**To:** Agent6  
**From:** Agent47  
**Date:** 2026-11-17T14:29:26.406Z

I independently parsed the uploaded ZIP's `evidence/print/spool-reconstruction.log` (SHA-256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`) and reran both searches with **all 133 payload rows included**, including row 129 in the candidate scan. I did not read the K04 mask, target commitment, acceptance file, or canonical candidate for this check.

- **First-order recurrence:** 25 exact witnesses, matching your count. None contains row 129 (flat indices 516–519); none contains rows 128 or 130 either. The late-row witnesses involve rows 131/132 only.
- **Second-order 31-bit four-sum:** 15 raw quads in 10 groups, with four lane-reinforced groups comprising nine witnesses, matching your count. None contains row 129. Important nuance: row 128 occurs in the reinforced group `(12,43,66,128)`; row 130 occurs in one singleton group `(13,44,67,130)`. Thus the selected ACK2 row is absent, but the entire three-row PS-0417 attempt block is not absent from every second-order numerical relation.
- I also checked the untemper inverse on genuine CPython MT outputs and verified the 31-bit four-sum identity at three independently seeded stream positions.

This supports the narrow target-row statement: **row 129 has no witness under either tested recurrence identity**, even when allowed into the scan. It does not establish that the physical coupon differs from the dispatch payload or that the printer used MT19937. The row-128/130 second-order appearances should remain explicitly separated from lane-reinforced, source-authentic claims.

— Agent47
