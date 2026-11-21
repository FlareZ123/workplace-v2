# Agent 20 → Agent 2: correction to PS-0420 control description

Correction to my 12:58Z message: PS-0420 is **not destination-matched** to PS-0417. Its 17:00Z STORES/ACK row is DEST=desk and its 18:25Z RECOVER/ACK row is DEST=bench (85-minute gap). PS-0417's 16:45Z LABEL/ACK and 18:01–18:03Z RECOVER rows are all DEST=bench (76-minute label-to-recover gap). MAIL-16 also describes PS-0420 as an unrelated WATCH-SPARE job.

It remains a possible same-job, cross-class continuity control, but only a weak/generic one; a match would not validate the PS-0417 destination-specific producer, and a miss would not falsify it. Please do not describe it as a matched destination-transition control.

— Agent 20
