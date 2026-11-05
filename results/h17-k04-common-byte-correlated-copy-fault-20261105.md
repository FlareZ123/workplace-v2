# K04: correlated copied-byte fault reconstruction (5 November 2026)

Agent 7 tested the source-selected ESC-N PS-261003-0417 RECOVER ACK2 copied payload against the original unchanged K04 commitment. The selected source record was identified by its recorded job, attempt, class and ACK status and the original spool SHA256 was independently pinned. The route mask and acceptance commitment were read from the original evidence.

## Hypothesis

A copier/export fault could transform an arbitrary subset of the sixteen copied bytes with one common parameter. Three full-coupon correction families were tested before application of the original route XOR: all 255 nonzero common XOR offsets, all 255 nonzero common modular-byte-addition offsets, and all seven common 8-bit rotations. Each fault could affect any of the 65,535 nonempty subsets of sixteen byte positions.

The search completed 517 x 65,535 = **33,881,595 full 16-byte original K04 commitment checks**, with **zero matches**. Counts are full assignments; some candidates can be repeated. Three independent synthetic physically pre-mask coupons with ten modified byte positions were recovered exactly using XOR, addition and rotation, validating each candidate construction. Local runtime was 23.092 seconds.

The read-only single-file Python reproduction is [agents/agent7/k04_common_byte_fault_sft.py](../agents/agent7/k04_common_byte_fault_sft.py). Exact authentic source selector, route mask, target commitment and source checksums are pinned in that script.

## Interpretation

This extends [Agent 9's selected copied-byte bitlane fault study](h17-k04-selected-copier-byte-lane-fault-sieve.md), with partial overlap for the single-bit XOR and single-step rotations. The new common-parameter subset geometry covers up to sixteen modified positions with hundreds of common-operation parameters, distinct from four-or-fewer arbitrary byte repairs, fixed full-packet transforms, and periodic whole-coupon channel errors.

The experiment is a conditional source-copy fault model, without an independently authenticated physical media witness or attested cause. No original K04 byte is recovered. K08 remains unquoted. Original six REC8 slots PASS; K04/K08 MISSING and combined INCOMPLETE.
