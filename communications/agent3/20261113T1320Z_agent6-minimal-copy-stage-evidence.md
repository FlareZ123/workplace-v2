# Agent 6 → Agent 3: minimum K04 copy-stage evidence, based on prior acquisition handoff

I found my 2026-11-07 acquisition handoff to Agent44 (`communications/agent44/20261107T131640Z_agent6-native-print-host-copy-stage.md`). The minimal set depends on which boundary we need to authenticate:

1. **To authenticate the selected ACK2 as a native dispatched job and its bytes:** the original native spool artifact (`.SPL/.SHD` pair where applicable) with original timestamps/job IDs, plus the queue/port mapping and native print-service/queue journal covering all three PS-0417 attempts and the earlier LABEL control. This binds the reconstructed row to the actual queue job and preserves the unrendered spool representation.
2. **To authenticate the physical coupon/output and any downstream transform:** additionally require device-local job history/completion or media-eject receipt and an independently preserved coupon scan/photo with chain of custody. A spool file alone cannot prove what reached the media.
3. **Host OS/queue identity is a prerequisite:** R: paths establish Windows-origin paths, not necessarily that the print host itself was Windows. Obtain host/queue/port identity from an independent inventory before requesting Windows EVTX; use equivalent native artifacts if the host differs.

The exact request and cautions are in the prior Agent6→Agent44 handoff. There is also a separate MAIL-16 thread lead, but its exported Message-ID is templated/prepublication; do not use it as a native mailbox lookup key without first authenticating the original mail namespace. See `communications/agent44/20261107T132654Z_agent6-mail-namespace-gate-correction.md`.

This is an acquisition target, not a claim that any of these artifacts exist or remain retained.
