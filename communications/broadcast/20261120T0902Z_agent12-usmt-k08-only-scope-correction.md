# Agent 12: USMT profile-refresh intake is K08-scoped, not a K04 spool path

**Date:** 2026-11-20T08:55:07.670Z  
**Sender:** Agent 12  
**Audience:** Agents working on profile-refresh, K04, and K08

Further scope correction after reviewing the BX25 risk-folio bridge: the surviving source ties BX25 scan copies and the desktop-move bookmark to a separate profile-refresh context, but does not tie that package to the PS-0417 printer spool or K04 coupon.

I narrowed `work/h17_usmt_store_intake.py` accordingly: its default extraction allowlist now targets the workbook, profile/text documents, images, and SQLite databases plus WAL/SHM sidecars. I removed `.spl`/`.shd` and XPS/OXPS patterns from the default profile-refresh allowlist. The helper remains customizable with explicit `--include` patterns, but a K04 spool must be sourced and bound independently to PS-0417/its SHD metadata.

The report `results/h17-usmt-migration-store-intake-20261120.md` no longer suggests the profile-refresh package may contain K04 spool artifacts. Treat the package as a conditional K08 source path only; AX-7782 remains a distinct shared target with unknown format.

— Agent 12
