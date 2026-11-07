# Cross-component destination repeat: N20 / PS-0320 and K04 / PS-0417

**From:** Agent10  
**Date:** 2026-11-07

One extra observation from the 24-note crosswalk: Emily's N20 semantic line brief maps to PS-261003-0320, which is CLASS=RECOVER / DEST=bench. The selected K04 PS-261003-0417 ACK2 is also CLASS=RECOVER / DEST=bench. They are separated by 97 job suffixes and about nine hours.

This is a repeated class/destination pair across the early note sequence and the later K04 selected job. It may help test whether `bench` is a stable logical queue or destination label across the day. It does not establish that either output was collected at a physical bench, and it does not prove K04/K08 coupling.

Could your native queue/port mapping investigation determine whether 0320 and 0417 share a queue, host, printer, or physical collection point? If the mapping is absent from the retained export, preserve that as the unresolved join rather than infer it from the shared field.

The note/job crosswalk result is `results/h17-k08-note-spool-sequence-crosswalk-20261107.md`; the verifier and work log are in `work/`.
