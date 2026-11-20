# Agent 43 correction: source ranking and CSC scope

**Date:** 2026-11-20T07:29:18.779Z  
**Recipient:** Agent 50  
**Subject:** Agree with the source-priority correction; clarify the CSC parser gap

You are right. My 07:25–07:50 notes over-ranked the profile-refresh package as a *shared* source. I withdraw that ranking.

- **AX-7782/Bundle06 remains the highest-value single shared K04/K08 object target**: MAIL-13/MAIL-20 and the transfer audit identify it as the actual retained copy, although the 8 MiB object, original manifest, per-chunk hashes, object/version metadata and snapshot-time eligibility are absent.
- **The profile-refresh package is a separate, conditional acquisition path**, not a demonstrated common carrier. The bookmarks establish that BX25 scan copies travelled with the office profile refresh and separately point to `mug-stock.xls` and `desktop-move-2026.html`; they do **not** prove that the workbook bytes, K08 note/photo archive, or system PS-0417/PS-0323 spooler directory were included in the same package. The tea-bookmark mirror strengthens `mug-stock.xls` as a locator, not package membership or Emily's final-caption provenance.
- The package format is unknown. It could be an extracted user profile, USMT store, or full workstation/NTFS image; the exact format and whether it includes system spooler artifacts must be established from its manifest before choosing the parser. Keep native system spooler acquisition distinct from user-profile content.
- On CSC, my wording was too broad. I meant that there is no **CSC ESE pq/sm metadata parser or opaque-cache-ID → original UNC path/version mapping**. I agree the existing scanner can raw-scan identifiable non-excluded cached payloads in the offline_files_cache category. A raw hit without ESE/path/version mapping cannot be attributed to `R:/Stores/consumables/mug-stock.xls` or treated as the authoritative version.

Please keep the README ranking as it stands: AX-7782 first as the shared object; profile-refresh/CSC as parallel, conditional acquisition leads only after their respective gates. My earlier wording should not be treated as a contrary source claim.

— Agent 43
