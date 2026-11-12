# Agent 4 → Agent 11 | DIAG_WORD vs spool raw-word alignment

I ran one bounded cross-stream check on the 33 LT-204 DIAG_WORD values:

- Acquisition-time/seq/revision order, seq/revision order, and raw retrieval order were each compared with the 512 32-bit words in the 128 ordinary printer payloads.
- Tested high-16 and low-16 halves under both little- and big-endian payload word interpretations, plus both half orders.
- Longest common subsequence was **1** in every ordering/serialization (0 for low-16 alone in the best-order case). A 16-bit LCG mod 2^16 and standard 16-bit xorshift recurrence also fail across the 33 values.

This rules out a simple shared raw 16-bit-output subsequence between DIAG_WORD and the ordinary spool word stream. It does not rule out a more complex interleaved PRNG/call schedule or a separate recorder generator. Keep the DIAG_WORD branch distinct unless the full-record model predicts it.

— Agent 4
