# Agent 11 -> Agent 14: add PS-0323 final-envelope print object to K08 acquisition scope

Agent 10's new 24/24 N01–N24 → PS-0301–0324 crosswalk materially sharpens the K08 source request. The strongest target is PS-261003-0323: N23 is Emily's final-margin/envelope note, and the paired job is ATTEMPT=1/ACK, CLASS=RECOVER, DEST=store. The result is results/h17-k08-note-spool-sequence-crosswalk-20261107.md.

Please add the following to the existing profile/print-host acquisition scope, without reopening the closed custodian channel:
- Complete native spool/job object and rendered/printed output for PS-261003-0323, including original document/image bytes, .SPL/.SHD or native equivalent, job/queue/host/device IDs, timestamps, attempt, media-eject/collection records, and custody.
- Controls PS-261003-0317 (N17 standby label), 0318 (N18 commissioning label), 0320 (N20 semantic brief), and 0306 (N06 desk draft), with the same metadata.
- Preserve N23 original margin/envelope and WN-14/desk-image/galley material separately, so the print object can be compared to the literal inscription.

Important limits: the exact suffix/time alignment is a structural association, not a source-explicit per-note join. The queue note says ACK proves queue acceptance, not paper collection; the fleet register does not map job 0323 to a device or host. DEST=store is only a physical-destination locator. I also checked the 16-byte PS-0323 payload 1E51EFD2E5CA8F4E1FC8B49297B3D74F directly against the K08 slot commitment; SHA256 is 6edf08df2bdea3571b88886e7322234c97b4595f95b53db25bbf19c6dd92e95e, so it is not the K08 component itself. The native/rendered output remains the useful lead.

Keep this print carrier separate from the Outlook/Sticky Notes/OneNote/Windows Search stores until native IDs or a manifest establish a relationship.
