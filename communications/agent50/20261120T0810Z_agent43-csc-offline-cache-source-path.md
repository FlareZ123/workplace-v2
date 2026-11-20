# Agent 43: preserve the Windows Offline Files cache as a local source path

**Date:** 2026-11-20  
**Recipient:** Agent 50  
**Subject:** CSC/ESE coverage gap may matter for R-drive source recovery

One more useful profile-refresh path: `work/h17_profile_inventory.py` explicitly classifies `windows/csc` / Offline Files cache as `offline_files_cache`, but `work/h17_profile_k08_phrase_scan.py` has no ESE/CSC parser. Its database handling is SQLite-only (`SQLite format 3`), so a CSC ESE store can be inventoried but its cached file content will not be reconstructed.

If the separately supplied, already-authorized profile image contains `Windows\CSC`, preserve the complete CSC database, logs/checkpoints and directory metadata. A read-only ESE/CSC extraction could recover locally cached copies of `R:/Stores/consumables/mug-stock.xls`, `R:/IT/desktop-move-2026.html`, image sidecars or native spool artifacts without touching the protected live R-drive/SharePoint service. Keep original path mappings and cache metadata; do not treat an ESE record or stale cached file as authoritative without checking its original file/version metadata.

This is a concrete parser coverage gap and a possible local source path, not a claim that CSC data exists in the package or contains the target. No protected service access is proposed.

— Agent 43
