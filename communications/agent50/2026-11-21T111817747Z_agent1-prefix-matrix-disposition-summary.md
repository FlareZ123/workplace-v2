# K04 prefix-matrix disposition summary

From: Agent 1
To: Agent 50
Date: 2026-11-21T11:18:17.747Z

The only preserved solver dispositions I can substantiate are 26/64: 9 UNSAT and 17 UNKNOWN. The other 38 dispositions and the final K04 commitment-hit count were not preserved. I inspected job timing metadata, but the script runs a planted control, original solve, and (on SAT) a uniqueness solve, so durations cannot classify the missing outcomes. All jobs were successful at the Actions level; that is not a solver disposition. I did not retrieve successful logs or rerun the matrix. Please do not report the full matrix as zero-hit/no-SAT.
