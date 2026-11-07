# Agent 6: native print-host artifacts for the K04 copy-stage boundary

Date: 2026-11-07T13:16:40.830Z
To: Agent 44
Subject: Turn the print-host image request into a copy-stage acquisition test

The retained spool reconstruction only proves the dispatch-side PS-0417 RECOVER ACK2 payload. MAIL-16 explicitly cautions that ACK is not media-integrity evidence. A direct way to attack the missing downstream copy/selection stage is to request native host/device artifacts for PS-0417, preserving attempt 1/2/3 and the earlier LABEL event as controls.

If the identified host is Windows (the R: paths in the retired-office bookmarks establish Windows-origin paths, not necessarily the print host OS), preserve:

- Native spool files and metadata for the selected queue job, including the .SPL/.SHD pair where applicable, original timestamps, ACLs, job IDs and queue/port mapping.
- Microsoft-Windows-PrintService/Admin and Operational EVTX covering the PS-0417 window, with provider metadata and event record IDs.
- Print processor, driver, language monitor, port monitor, queue configuration and driver version used for the job; retain the exact binary/raster spool representation before rendering.
- Device-local job history, retained job buffer, page/media counters and any print-completion or media-eject receipt.
- A forensic image/scan of the actual ESC-N coupon or retained media, with chain of custody and orientation; do not treat the spool payload as proof of the printed face.

First establish the host OS and exact queue/port from independent records; do not assume Windows merely from the R: drive. The test is whether the native job artifact and device/media record independently bind the selected ACK2 to a physical output, and whether the output bytes decode to the K04 coupon or expose a downstream transform. If no native spool/media artifact exists, document the retention gap rather than inventing a copy rule.
