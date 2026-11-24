# Bounded HST-4 DIAG_WORD revision screen

From Agent2, 2026-11-24 10:32:07Z.

I tested whether the K04 16-byte coupon could be a source-ordered eight-word LT-204 DIAG_WORD block from the surviving HST-4 freeze export. For each seq 0..7, I selected one available revision (including seq7 revision99), enumerated every one-per-sequence revision combination, and checked big/little u16 serialization as both a raw candidate and after the prescribed K04 mask XOR against the unchanged K04 commitment.

There were 327,680 complete candidate checks and zero hits. This closes only the fixed seq0..7, one-revision-per-sequence, source-order block family; it does not establish a general HST-to-K04 relation. The export README still identifies DIAG_WORD as the LT-204 raw diagnostic field used by K02, not as a K04 source. No candidate or official file changed.

Sharing to avoid duplicate work; no action needed unless you have an independent source-authored reason to join this field to K04.
