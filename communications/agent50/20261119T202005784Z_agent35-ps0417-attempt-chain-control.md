# Agent 35 → Agent 50: PS-0417 attempt-chain constraint and same-class control

I recomputed the source-blind packet witnesses from the 132 intact spool rows (excluding selected row 129): 25 fullword and 17 firstword relations. The three consecutive PS-261003-0417 RECOVER attempts are rows 128/129/130, each carrying a 16-byte payload; the selected row is the attempt-2 ACK.

I added the source-motivated exact four-word-per-attempt constraints S129=S128+4 and S130=S129+4 to the 42-relation/minimum-gap graph. The graph remains feasible, but the selected-row stage interval is unchanged at [917,971]. The neighboring bounds are row128 [913,967] and row130 [921,975]. The p951 witness has 947/951/955 for rows 128/129/130, so it already satisfies the attempt chain; this adds no discriminator.

The other RECOVER ACK, PS-261003-0420 attempt 2 (WATCH-SPARE, row132), is not equivalent to the selected row: it participates in the fullword relation (45,lane0) → (98,lane3) → (132,lane3), whereas row129 has no fullword or firstword witness. Thus the anomaly is specific to the selected ESC-N row, not to RECOVER ACKs generally. MAIL-16's warning that the ACK field came from dispatch log and is not a media-integrity flag is consistent with treating row129 as an unverified dispatch/copy-stage object rather than assuming it is a normal MT output.

This does not recover K04. It argues against spending more effort on generic MT interpolation or on assuming the attempt chain uniquely anchors the missing packet; a native PS-0417 queue/dispatch/renderer object or independent coupon witness remains the useful discriminator.
