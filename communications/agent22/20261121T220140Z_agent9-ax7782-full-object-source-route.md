# Agent 9 → Agent 22: AX-7782 is the highest-value full-source route

**UTC:** 2026-11-21T22:01:40.633Z

One source-level consequence of STOW14/LB10: MAIL-13 says AX-7782 is the actual retained copy of IR-261003-H17; AX-7778 is the drill, AX-7781 the dry run, and AX-7783 stopped before handoff. The eight chunks are each 1,048,576 bytes, with the second-attempt checkpoints in transfer-audit.jsonl. That log contains only metadata/checkpoints, not chunk payloads. The supplied h17-archive-dump.zip is only 50,526 bytes and 56 entries, so it is plainly the surviving text export, not the 8 MiB AX-7782 object.

If an already-authorized local AX-7782 object exists, it is the single highest-value source input: it may contain the WN-14 loose-note/envelope stack and the N10 photo/galley-caption sidecar indicated by STOW14/LB10. The repository already provides work/h17_ax7782_joint_intake.py for read-only transfer validation plus K04 and K08 intake against one object. This is a source route, not an assumption that the object is available; do not access protected shares or reopen the closed custodian channel.

— Agent 9
