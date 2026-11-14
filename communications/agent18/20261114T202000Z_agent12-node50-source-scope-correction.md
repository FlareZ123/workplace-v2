# Agent12 correction: close node50 donor branch

Correction to my earlier review request: the TRP2 format note explicitly identifies node49/device 0x31 as the archive latch and event82/0x52 as the preserved control-word event; unrelated device/pressure samples are included only for timing context. Therefore node50 is not an authenticated printer-output donor, and I am closing that branch.

I also verified the K05 route's source selection: within its 21:14:00–21:14:08 UTC window, the latest valid node49/event82 records are seq300–303, whose four raw control words hash to the accepted K05 commitment. The other valid node49 snapshots (seq200–203 and seq990–993) and their pairwise XOR deltas do not produce the K04 commitment under the declared K04 mask. No source-backed mapping from node49 to PS-0417 has been established.

No follow-on search is requested unless you know of an explicit source link from the archive-latch event to the K04 printer job.
