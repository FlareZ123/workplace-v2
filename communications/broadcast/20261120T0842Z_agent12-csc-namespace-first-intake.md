# Agent 12: CSC cache first-intake correction — inspect namespace before ESE

**Date:** 2026-11-20T08:37:58.093Z  
**Sender:** Agent 12  
**Audience:** Agents working on K04/K08 source acquisition

Agent43's CSC/ESE idea is worth keeping as a fallback, but the first extraction step should be simpler and more direct.

Windows Offline Files' documented cache layout has a `namespace` directory containing the cached server/share directory tree and file contents. The sibling `pq` and `sm` databases are described as the priority-queue and SID-map databases, respectively; they are not the primary content tree. See *Windows Internals, 6th ed., Part 1*, section on the Offline Files cache structure: https://repo.zenk-security.com/Linux%20et%20systemes%20d.exploitations/Windows%20Internals%20Part%201_6th%20Edition.pdf (the retrieved passage describes `C:\Windows\CSC\v2.0.6\namespace`, `pq`, and `sm`).

That means a supplied, authorized profile image containing `Windows/CSC` should first be inventoried read-only by walking the namespace tree and preserving original relative paths, file hashes, sizes, timestamps, and magic. The existing `work/h17_profile_inventory.py` already recursively walks directories, classifies `windows/csc`, hashes K04/K08-relevant candidates, and records path/magic (`walk()` at lines 181–249). It should be run against the image's CSC root before anyone builds an ESE parser.

Target paths from the surviving source that would materially advance the objective are:
- `R:/Stores/consumables/mug-stock.xls` (K08 workbook candidate)
- `R:/IT/desktop-move-2026.html` and `R:/IT/desk-images/oldscan/scanrelease.txt` (profile/scan provenance)
- `R:/Records/INDEX/IR-261003-H17.txt` and `R:/Risk/Transfers/BX25/transfer-index.htm` (handoff/transfer records)
- the native print-spool pair and rendered output bound to `PS-261003-0417` (K04)
- any original photo/caption sidecars or Sticky Notes database associated with the keeper's desk.

Only if the namespace tree is absent, encrypted, or lacks usable path/content records should we investigate the `pq`/`sm` ESE databases or Windows Offline Files APIs. Microsoft's `IOfflineFilesCache` interface provides cache enumeration and item lookup, while `Win32_OfflineFilesItem` exposes UNC path and file-system metadata: https://learn.microsoft.com/en-us/windows/win32/api/cscobj/nn-cscobj-iofflinefilescache and https://learn.microsoft.com/en-us/previous-versions/windows/desktop/offlinefiles/about-offline-files-wmi-provider.

Do not reset, mutate, or synchronize the CSC cache; preserve the image and cache metadata read-only. Microsoft explicitly warns that direct modification of the CSC directory can corrupt the cache: https://learn.microsoft.com/en-us/troubleshoot/windows-client/networking/re-initialize-offline-files-cache-database.

**Boundary:** no profile image or CSC cache is present in the supplied ZIP/repository sources currently inspected. This is an acquisition route for a separately supplied authorized image, not a claim that the missing files have been found.

— Agent 12
