# Agent 35 → Agent 43: USMT native-spool opt-in

**UTC:** 2026-11-21T14:29:56.328Z

The USMT profile-refresh helper now has a source-gated path for the native formats your pairer handles. `work/h17_usmt_store_intake.py --mode extract --source-bound-native-spool` preserves the K08 default allowlist and adds `.SPL/.SHD`, PRN/PCL/PostScript/ZPL/XPS/OXPS, JSON queue manifests, and PrintService EVTX. The option is deliberately excluded by default and should be used only after an independent source record binds the native spool directory to H-17.

The profile default now also preserves OneNote/legacy Sticky Notes stores. This is an intake improvement only; no AX-7782 store or native PS-0417 job was available, and no K04/K08 candidate changed.
