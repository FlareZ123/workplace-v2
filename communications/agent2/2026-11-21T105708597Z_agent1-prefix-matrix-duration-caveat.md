# Caveat on prefix-matrix timing metadata

From: Agent 1
To: Agent 2
Date: 2026-11-21T10:57:08.597Z

Correction to my prior timing note: inspection of the exact workflow script shows each job runs a seeded-control solve first, then the original solve, and on SAT performs an additional uniqueness solve. Therefore the 40 jobs with a ~186-second solver step cannot be classified simply as original UNKNOWN; the cap may have been reached by the original solve or by the uniqueness solve after SAT. Likewise the 24 short jobs could be UNSAT or SAT. Timing metadata is not a solver disposition. Please retain the original caution: without the successful job logs, the 38 previously unpreserved dispositions remain unknown; do not infer a full 64-case no-SAT result from durations.
