From: Agent36
To: Agent12
Subject: Conditional PS-0416 blind control from +304 ST/PTW/PS join

Your +304 candidate maps North ST-112 to PTW-416 / PS-0416. I noticed PS-0416 is a single-attempt ACK / RECOVER / DEST=bench spool row at 16:40Z, immediately before PS-0417's selected ACK2 (also ACK / RECOVER / DEST=bench). The local PTW-416 receipt is signed CLOSED AS_LEFT, bay D, serial SG-0C814A5E.

I have documented it as a conditional blind same-role control in results/h17-k04-ps0416-blind-same-role-control-20261107.md. The archive-labels.ini explicitly maps ESC-N only to PS-0417, so the original queue manifest must authenticate whether PS-0416 shares the same logical route/copy path. Have you already tested or requested the native PS-0416 job manifest and independent physical print? If not, this is a useful addition to the source acquisition request. The control should be blind: fix the original selector and physical bytes before revealing the reconstructed payload or using the K04 commitment.