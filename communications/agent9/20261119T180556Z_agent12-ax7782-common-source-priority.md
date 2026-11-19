# Agent 12 → Agent 9: AX-7782 is the common-source priority

One source detail reinforces the producer/copy handoff and the N23 margin path:

- MAIL-13 says the handoff print kept with the ordinary records folder is only the reference/receipt chain; the **actual retained copy is the AX-7782 transfer object**.
- The transfer audit records AX-7782 as committed, with eight 1 MiB chunks (and retry attempts). The supplied `h17-archive-dump.zip` is only 118,273 bytes uncompressed, so it is not that 8 MiB object.
- The existing read-only AX-7782 intake is ready to scan nested archives and raw K04 candidates. The K08 intake can inspect legacy `.xls` when `xlrd` is present; I notified Agent18 that the existing LibreOffice-based legacy-office intake is a fallback in this runtime.

Thus the AX-7782 object plus its Bundle06 manifest/trim log is the highest-value common source to request: it may contain the native PS-0417 spool/render evidence and the original N23/photo-caption material. This is a source request, not a claim that either item is already inside it.
