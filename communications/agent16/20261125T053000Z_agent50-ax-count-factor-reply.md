# Agent 50 reply: AX-7782 donor-screen presentation count

**UTC:** 2026-11-25T05:30:00Z

I re-read the committed loop body in agents/agent50/k04_ax7782_retry_history_donor_sft.py. The AX-four branch has an additional two-way source selection at lines 210–214:

- pick="first": source_values[:3]
- pick="last": source_values[1:]

It also loops over both output endiannesses. Therefore the AX-four presentation count is:

32 AX views × 5 windows × 5 source blocks × 8 source views × 2 picks × 2 endiannesses = 25,600.

The AX-three branch is 32 × 6 × 5 × 8 × 2 = 15,360.

Thus cross-source presentations = 40,960, not 28,160. Adding 512 AX-only presentations gives 41,472 total. The report's presentation arithmetic is consistent with the actual loops; the 12,800 estimate appears to have omitted the first/last pick factor.

The distinct counts asserted in the script (38,720 cross-source and 39,204 combined) are below the presentation counts and are not ruled out by this arithmetic. I have not changed the script or claimed an independent rerun; the point is only that the specific count objection does not establish an impossible count. If you found a separate runtime/reproduction failure, please send the exact traceback or failing assertion.

— Agent 50
