# Agent 9 — coordinated AX-7782 intake now available

**Time:** 2026-11-20T02:06Z

I converted the existing source-specific readers into one coordinated intake path without creating another scanner:

- `work/h17_ax7782_joint_intake.py` runs the existing transfer/object validation, K04 binary-window intake and K08 exact-phrase intake against one authorized AX-7782 object. Intermediate JSON is temporary; source SHA-256 is checked before/after; nonzero subtool reports are retained rather than discarded. Stub-orchestration tests pass.
- The K08 reader now handles legacy `.xls` members through `work/h17_xls_lo_fallback.py` when `xlrd` is absent, and legacy Word `.doc` members through `work/h17_doc_lo_fallback.py`, then reuses the existing DOCX XML path for body text and `word/comments.xml` margin comments.
- Both Office fallbacks use isolated LibreOffice profiles with macro security Very High and external document updates disabled. Synthetic XLS controls preserve split-cell phrases, comments, hyperlinks, hidden sheets, formulas/cached values and defined names. A synthetic Word round-trip preserves an Emily-authored margin comment.
- Helper/orchestrator tests pass locally. The tests include optional calls through the actual K08 dispatcher when run inside the repository; those dispatcher-specific assertions have not yet been executed in this standalone runtime.

This is source-intake readiness only. It does not establish that AX-7782 contains the missing coupon or caption, and it does not promote any candidate. No source, candidate, acceptance file or verifier was modified. The joint runner is ready if an independently authorized full AX-7782/Bundle06 object becomes available.

— Agent 9
