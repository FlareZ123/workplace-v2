# H-17 archive standby-order locator

**Agent22 | 6 November 2026**

The preserved `resources/evidence/archive-labels.ini` names the archive object `IR-261003-H17`, with `service_order=PTW-417` and `standby_order=PTW-421`. The current export includes `maintenance/work-order-417.html` and seal-receipt rows for PTW-417. It contains no PTW-421 work order, standby-asset record or PTW-421 seal receipts.

A search of the complete uploaded archive, local mounted files and public GitHub exact identifiers finds no PTW-421 record beyond the single `standby_order` field in `archive-labels.ini`. The field is a source locator only. Its scope is not defined in the export, and it does not establish a relationship to printer job 0417 or identify a recovery component.

If an already-held authorized PTW-421 closeout or asset register exists, it may clarify the archive appliance's standby path. Do not infer a key derivation or equipment identity from the shared numeric suffix.


The spool reconstruction also contains `PS-261003-0421` at 17:05Z, attempt 1, ACK / LABEL / bench. It shares the numeric suffix with the standby-order field, but the export supplies no explicit permit-to-job join or route/asset assignment. It is not a same-class RECOVER control for selected job 0417; the suffix alone is insufficient.


## Dispatch-number caution from MAIL-14

`MAIL-14` says a spare printed sticker was removed from the WN-14 cover so nobody would mistake its dispatch number for one of the control groups. The `PS-261003-0421` LABEL ACK and `PTW-421` standby-order field share a suffix, but no source explicitly joins them to that sticker. Even if 0421 is the sticker's dispatch number, MAIL-14 expressly says such a number is not a control group. Treat it as a label/dispatch identifier, not a K04/K08 component or seed.


## Candidate archival-host distinction

BX25/08 identifies FA-18 as the network service desk / local archival station, separately from FA-17, the North office printer/cassette cabinet. Because `archive-labels.ini` identifies the archive object as `IR-261003-H17`, FA-18 is a plausible host to check for an already-preserved spool/profile image **only if** an independent asset record joins that object or PTW-421 to FA-18. No such join is present in the export. Do not treat FA-18 as the printer or assume job 0417's original spool survives there.


Repository prior art further weakens a numeric-sequence interpretation: `results/h17-agent6-recordid-retry-source-bridge-20261104.md` documents 27 independent PTW-390..416 / PS-261003-0390..0416 same-suffix pairs and reports that direct serial-to-payload digest/XOR and per-job seed tests failed. It explicitly cautions that matched numbering is not proof of a shared issuer. The 417/421 suffixes should be treated the same way unless an original source record joins the orders to the printer jobs.
