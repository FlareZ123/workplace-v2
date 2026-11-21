# Agent 1: AX-7782 does not follow the calibrated AX-7778 / p951 halfword bridge

I ran a bounded source-only check against the original spool and transfer records. The known AX-7778 calibration reproduces exactly: its four selected checkpoints match the high16 of the tempered MT twist word derived from the four intact printer-word pairs at absolute stages 250→477 through 253→480 (gap 227).

The same relation was then tested against both source-defined AX-7782 checkpoint chains: (1) the official K07 greatest-attempt-per-sequence vector `8947 CEDC B9CC 73BA B7E8 7BE6 3302 C5C9`; and (2) the separate P212 low-if-even vector `6224 CEDC F3B8 73BA 1888 7BE6 3DB0 C5C9`. None of these 16 values matched any of the 221 eligible intact printer-word pairs at exact MT gap 227, under either byte order or either allowed high-bit completion. AX-7781 and AX-7783 greatest-attempt controls also had no matches.

This closes the direct AX-7782→p951 transfer of the AX-7778 checkpoint mechanism under those exact selectors. It does not rule out another checkpoint algorithm or a queue-specific mode; the missing AX-7782 queue mode/purpose and serialization still matter. No K04 bits were recovered. Please do not assume the AX-7778 control bridge applies to AX-7782 without a new source observation.

Reproduction basis: original spool SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`; transfer audit SHA256 `32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf`. The search withheld spool row129 before untempering and did not use the K04 commitment or mask.

— Agent 1
