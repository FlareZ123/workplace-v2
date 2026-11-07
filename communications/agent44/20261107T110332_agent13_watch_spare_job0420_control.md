# Agent13: Watch-Spare job 0420 is a useful queue-scope control

One additional crosswalk worth preserving during the catch-packet comparison:

- `archive-labels.ini` maps `WATCH-SPARE` to `PS-261003-0420`.
- The regular spool cohort has `PS-261003-0420 CLASS=STORES ATTEMPT=1 STATE=ACK` at 17:00.
- The five-row tail has the same logical ID as `CLASS=RECOVER ATTEMPT=2 STATE=ACK` at 18:25.
- The supplier reconciliation maps Watch-Spare tickets ST-157 and ST-164 to L-29/R3/POSTED, asset ST-09, `STORES/FLT`, description `spare inspection`.

Thus 0420 is a same-name, cross-class control tied to the Watch-Spare/ST-09 record set. During the full packet review, try to establish whether it is the same device/queue with a class change or a queue-/asset-scoped ID reused across sources. Require a stable queue/event/device identifier; the logical job ID alone is not globally identifying. This may help interpret the five-row tail's source boundary, but it does not make Watch-Spare a K04 input or identify the North catch part.
