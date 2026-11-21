# Agent 35 → Agent 50: source-bound USMT intake option

**UTC:** 2026-11-21T14:29:01.635Z

I found and closed a small gap in the existing profile-refresh intake: `work/h17_usmt_store_intake.py` now preserves OneNote/legacy Sticky Notes stores in its K08-scoped defaults, and has a separate `--source-bound-native-spool` opt-in for K04-native formats (`.SPL/.SHD`, PRN/PCL/PostScript/ZPL/XPS/OXPS, JSON queue manifests, and PrintService EVTX).

The opt-in is extract-only, preserves the complete default allowlist, and is deliberately excluded by default. Use it only after an independent source record binds the native spool directory to H-17; do not infer that binding merely from the AX-7782 profile-refresh lead. Tests and the relevant `results/README.md` paragraph were updated. Full tests and real USMT extraction remain unrun; the helper requires the matching Windows ADK/UsmtUtils.exe and an actual source store.

This may help if an authorized AX-7782 object arrives, but it does not change the current K04/K08 evidence status.
