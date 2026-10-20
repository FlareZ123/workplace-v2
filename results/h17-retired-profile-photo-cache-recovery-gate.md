# H-17 K08 / incident-index recovery: retired Windows profile's residual search and photo preview artifacts

**Agent 21 | 20 October 2026 | Conditional original-witness acquisition plan.** This is a **new secondary digital-survival class**, not another HMAC phrase enumeration and not evidence that such an image exists. **No K04 coupon bits or exact K08 words have been recovered.** The original six accepted slots and unmodified verifier remain unchanged.

## Distinct source anchor

The newly supplied `resources/evidence/h17-supplemental-office-files/retired-office-bookmarks.html` declares itself an **office desktop migration, cached browser favorites from September 2026**. It includes:

- `file:///R:/Records/INDEX/IR-261003-H17.txt`, titled **Incident desk export index**;
- `file:///R:/IT/desktop-move-2026.html`, titled **Profile-replacement calendar**;
- `file:///R:/IT/desk-images/oldscan/scanrelease.txt`, titled **Desktop scanner release notes**.

The September labeling and October-3 incident filename are a *chronological provenance question*, not proof of impossible access: a bookmark cache might have been exported after a September migration began, or the title/file might have been revised. Preserve creation, export and file-system timestamps before interpreting them.

The primary source `evidence/mail/11.eml` explicitly says Emily worked from **desk notes and photograph captions**. Note N10 identifies revisiting a photograph; N23 says final words were written in her margin; `mail/20.eml` warns that the supplied bundle was trimmed. Source evidence does **not** prove the retired office profile belonged to Emily, that any photograph ever resided on that profile, that Windows was the photo-editing operating system, or that the final envelope margin was imaged. The only warranted bridge is a contemporaneous **retiring desktop/profile evidence class**, with a specific historical incident-records locator.

## New recovery mechanism (secondary traces, even if source original is absent)

Prior intake [v2 Issue #1](https://github.com/FlareZ123/workplace-v2/issues/1) already requests the native 2026 photographs, photo caption sidecars/editorial history and the final incident envelope, plus a preserved Windows print-host `.SPL/.SHD` copy for K04. This proposal instead preserves **secondary artifacts of a retired Windows user profile** that may survive after those original items have been moved, deleted or omitted from a ZIP export:

1. **Windows Explorer thumbnail database:** `Users/<profile>/AppData/Local/Microsoft/Windows/Explorer/thumbcache_*.db` and `thumbcache_idx.db`, in an **existing authorized historical disk image**, including volume-snapshot copies if present. Depending on the files previewed, a cache can retain a reduced image even if its source photo no longer exists. Forensic parsing must retain an independent path/date association, because a thumbnail alone does not establish the original filename or final-caption status. Particularly target images of the H-17 night desk, handwritten keeper margin, incident-envelope face and original N01/N10 photo material. A low-resolution thumbnail may not preserve legible text; do not hallucinate unreadable words.
2. **Windows Search index and transaction artifacts:** if that historical snapshot was Windows 10, the system index is commonly `ProgramData/Microsoft/Search/Data/Applications/Windows/Windows.edb`; on Windows 11 `Windows.db` is the official Microsoft-documented name. Preserve the **actual** version present, plus its accompanying logs/sidecar files and any already-retained shadow-copy versions. The index may retain paths, media metadata, photo titles/captions, email fragments or text snippets of the missing `R:/Records/INDEX/IR-261003-H17.txt` if the relevant location or attachment was indexed. Search presence and historical content are conditional on index scope and retention.
3. **Original photo-manager catalogue/caption project and sidecars:** preserve only authentic catalogue files, application state and `.xmp` or equivalent metadata files actually observed on the historical snapshot. These may preserve **prior caption versions and edit history**, distinguishing draft from final when an independent dated link to the actual keeper envelope is available. Do not invent a particular photo application/database as present.

These are **read-only original-record acquisitions** for a qualified authorized custodian. Do not log into current devices, reactivate an old R: share, contact the current live workstation, alter indexed files or rebuild caches. Preserve an entire already-existing image/snapshot as acquired with SHA-256, dates, profile identity and custody chain before secondary analysis. An expert should perform forensic extraction on a copy.

## Specific blinded falsifier and expected target information

Before interpreting any potential K08 phrase, first independently link the disk/profile evidence to the archived `retired-office-bookmarks.html` identity, timestamp its copy and document any credible historical provenance. A scene photo or extracted caption is **not inherently the keeper's finally chosen line**. Require contemporaneous file metadata, margin/envelope context or final version attribution separating N02/N06 drafts and N17/N18 other-envelope labels. If the full final normalized phrase is demonstrably recovered, preserve the original raw visual/metadata bytes and version history, then apply the unchanged nonce-HMAC/SHA256 check. This may recover exact K08 words; otherwise **new attested final words remain zero**.

For the missing historical R: incident index, recover original text if present and follow only **historical preserved/offline references** into already authorized custody. An index mentioning ESC-N, `PS-261003-0417` or 18:02 UTC can direct a K04 original media/coupon search, but its existence alone does not give the 16-byte coupon. Independently authenticated coupon bytes would need the unchanged K04 reduction and commitment.

**Negative decision:** if no source-linked preserved desktop profile exists, or existing index/thumbnail/catalogue records have no relevant historical document or legible final words, stop this class. It is a *proposed acquisition path* and adds no source-specified target bytes today.

## External technical references (generic capability, not proof of H-17 provenance)

- Microsoft, [Troubleshoot Windows Search performance](https://learn.microsoft.com/en-us/troubleshoot/windows-client/shell-experience/windows-search-performance-issues) (2026): the default Windows index location, and the `Windows.edb` Windows 10 versus `Windows.db` Windows 11 names.
- Microsoft, [Windows Imaging Component integration with Windows Thumbnail Cache and Photo Gallery](https://learn.microsoft.com/en-us/windows/win32/wic/-wic-integrationregentries): how image metadata and thumbnails are exposed to Explorer/Photo Gallery.
- [Forensics Wiki, Windows thumbcache](https://forensics.wiki/windows_thumbcache/): Explorer thumbnail database location, extraction and challenges tying a thumbnail to a filename.
- [Windows Search forensic artifact overview](https://www.windowsforensics.app/en/artifacts/windows-search-index): scoped description of indexed paths, timestamps, content and deleted-data remnants. Third-party forensic resource; validate specific schema against the preserved OS image.

**Recovery accounting:** new authenticated original `PS-261003-0417` coupon bits: **0/128**. Exact final K08 words: **0**. REC8: **six PASS; K04/K08 MISSING; combined INCOMPLETE**. This document is a new preservation lead for *already-held historical media* only, not a claim that the missing originals are accessible or that any source has been delivered to a records custodian.
