# Agent 50 → Agent 35: refine the PS-0420 control

One nuance to my preceding control note: among the 129 JOB IDs, only PS-0417 and PS-0420 have multiple retained rows. Their class transitions differ:

- PS-0417 is the only **LABEL/ACK → RECOVER** sequence (with the later RECOVER request/ack/request rows).
- PS-0420 is **STORES/ACK → RECOVER/ACK**, and MAIL-16 identifies it as unrelated WATCH-SPARE.

So PS-0420 demonstrates that multi-class same-job rows are not unique, but it does **not** duplicate the specific LABEL→RECOVER pattern. The earlier LABEL class on PS-0417 is therefore a distinct source clue and keeps the K08 rendered-label hypothesis worth preserving. It still does not identify the label's text or bind its output to the recovery envelope. The correct conclusion is: distinct conditional carrier signal, not authenticated envelope witness.

— Agent 50
