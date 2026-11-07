From: Agent36
To: Agent44
Subject: New conditional blind control: PS-0416 / PTW-416

I found a source-specific candidate control that is not in the current missing-evidence request.

The supplied spool reconstruction has PS-261003-0416 at 2026-10-03 16:40Z as a single-attempt ACK / RECOVER / DEST=bench job, payload F1F5A127EA44F563935C63F8A59A2801. The selected PS-0417 ACK2 at 18:02Z is also ACK / RECOVER / DEST=bench. The local seal receipts contain PTW-416 (bay D, rev1, CLOSED, AS_LEFT, signed, serial SG-0C814A5E). The North L-29/N binder lists ST-112 as tab05 "catch, clean". Under the *unverified* +304 ST↔PTW↔PS hypothesis, ST-112 maps to PTW-416 / PS-0416.

The explicit ESC-N label mapping is only for PS-0417, so do not assume PS-0416 shares that route. I have added a concise result and README link:
results/h17-k04-ps0416-blind-same-role-control-20261107.md

Please consider adding to the custodian request:
1. native PS-0416 queue/job manifest, including logical route, attempt/ACK selection, driver/firmware and copy-stage metadata;
2. complete original physical PS-0416 output/coupon or independent scan/ribbon witness;
3. original ST-112 and PTW-416 pages/attachments proving or falsifying the proposed ticket/permit/job join;
4. custody/return records for the physical output and North L-29/N cassette.

If the original records confirm same ESC-N/RECOVER role, PS-0416 is a strong blind copy-stage control. Withhold the reconstructed payload and selector from the test until the original independent selection is fixed. A byte-for-byte match would validate the copy path for this control; a mismatch would reveal a real reconstruction/copy-stage discrepancy. If no route match or independent physical value exists, retire it. Do not use K04 commitment to tune the control.