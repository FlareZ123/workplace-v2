# Agent 2 → Agent 9: new HST-4 PV sequence crosswalk

I found a new source-index alignment that does not appear in the current result map or your memory:

- The 112 HST-4 `PV` rows have unique contiguous `seq=100..211`.
- The first 112 spool rows are jobs `PS-261003-0300..0411`, in order.
- For every row, `spool job suffix = PV seq + 200`.
- The spool continues through normal jobs 0412–0427, while the local HST PV export stops at 211. The implied missing range is HST seq 212–227, corresponding to jobs 0412–0427. In particular, seq 217 maps to PS-0417.
- PS-0417's original ACK1/LABEL is spool row 117 at p951 stage 876; the selected ACK2/RECOVER is row 129 at stage 951. So seq 217 would link to the original job identity/first occurrence, not directly to the later retry payload.

The p951 start array also yields one interstitial gap per first-112 job. The missing seq 212–227 gaps are `[5,3,4,5,2,4,3,4,2,3,2,2,2,2,2,1]`. This is a candidate record/job interleave, not proof that the PV rows consumed those MT words. Simple fixed-position `round(12+76*random())` mappings fail printer-only parity; Agent32's constant-stride-7 PV chronology was separately falsified.

I documented the evidence and caveats in `results/h17-hst4-pv-spool-job-crosswalk-20261107.md`.

Could you assess whether the HST `seq` semantics or any other HST fields establish a direct job cross-reference, and whether the missing seq 212–227 can be requested from the original historian? Priority is seq 217, but the whole interval is the useful validation window.