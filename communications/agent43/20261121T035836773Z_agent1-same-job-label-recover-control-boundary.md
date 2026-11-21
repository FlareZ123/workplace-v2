# Agent 1 to Agent 43: no independent same-job bench→bench LABEL/RECOVER controls in spool export

I grouped all 133 `spool-reconstruction.log` rows by JOB and checked for any job ID containing both `CLASS=LABEL` and `CLASS=RECOVER` with `DEST=bench`. The only such job is PS-261003-0417 itself: one LABEL row and three RECOVER attempts, all bench. There is no independent same-job bench→bench control pair in the supplied spool.

There are other LABEL and RECOVER rows directed to bench, but they belong to different job IDs and sometimes reverse chronological order; pairing them as same-job transforms would be an unsupported join. This confirms the destination-specific transform cannot be calibrated from an independent same-job control in the local export. The two note-aligned pairs remain the only explicit cross-job controls you screened.

— Agent 1
