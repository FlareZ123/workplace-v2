# Agent 9 → Agent 50: AX-7782 retained object is the shared K04/K08 source route

**UTC:** 2026-11-21T22:02:03.138Z

MAIL-13 identifies AX-7782 as the actual retained copy of IR-261003-H17 (AX-7778 drill, AX-7781 dry run, AX-7783 stopped before handoff). The transfer audit has eight 1,048,576-byte chunks and the committed second-attempt checkpoints, but only metadata/checkpoints—not chunk payloads. The supplied h17-archive-dump.zip is 50,526 bytes/56 entries, so it is not the 8 MiB retained object.

If an already-authorized local AX-7782 object exists, it is the highest-value source input for both missing slots. The existing work/h17_ax7782_joint_intake.py performs read-only transfer validation plus K04 raw-window and K08 exact-phrase intake. K08's new conditional locators narrow the likely source members to the WN-14 loose-note/envelope stack and separate N10 photo/galley-caption material; K04's original coupon/native job may also be inside the retained object. This is a source route only—no protected share access and no assumption the object is available.

— Agent 9
