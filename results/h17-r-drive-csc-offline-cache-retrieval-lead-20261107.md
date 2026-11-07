# Conditional R: drive Offline Files / CSC retrieval lead

**Status:** source-acquisition hypothesis only. No CSC image, cached file, K04 bytes, or K08 words have been recovered.

## Source clue

The supplied `retired-office-bookmarks.html` contains 14 Windows file URLs under `file:///R:/`:

| Bookmark target | Potential relevance |
|---|---|
| `R:\Stores\returns\SEP26\index.htm` | September cassette returns; vendor ticket list and North/South binder pages |
| `R:\Stores\consumables\mug-stock.xls` | Tea-room stock sheets; possible desk/galley context |
| `R:\Finance\PrevERP\posted-items-26.xls` | Historical posted settlement items |
| `R:\Finance\PrevERP\reversal-register.htm` | Reversal register and possible custody/settlement trail |
| `R:\Finance\letterheads\EG-operator-2025.pdf` | Office letterhead index |
| `R:\Finance\PrevERP\bench-expenses-2025.xls` | Bench expense apportionments |
| `R:\Risk\H17-POL-17\renewal-ledger-2025.xlsx` | H-17 property renewal ledger and declared items |
| `R:\Risk\Transfers\BX25\transfer-index.htm` | 2025 risk scan transfer index |
| `R:\IT\desk-images\oldscan\scanrelease.txt` | Desktop scanner release notes; potentially relevant to BX25/08 |
| `R:\Risk\hired-plant\CS-18\loan-set-register.htm` | Hired-equipment certificates |
| `R:\Records\INDEX\IR-261003-H17.txt` | Incident desk export index |
| `R:\Records\blank-request-form.doc` | Records request form |
| `R:\IT\staff-groups\EG.htm` | Electrical-group roster |
| `R:\IT\desktop-move-2026.html` | Profile-replacement calendar |

The bookmark file's own description says the BX25 scan copies travelled with the office profile refresh. That is direct evidence of a profile-refresh connection, but it does not establish that the R: share, any particular file, or the CSC cache was copied. The incident index and the other referenced files are absent from the surviving ZIP. The current acquisition request already calls for the historical R: mapping and a retired workstation image, but does not explicitly name the Windows Client-Side Cache (CSC). A bounded source-wide text scan of the surviving export for R: references, UNC paths, CSC, Offline Files, mapped-drive and network-share terms found no UNC target or CSC/Offline Files configuration evidence beyond the bookmark URLs. The local export therefore cannot resolve the R: mapping or this cache gate.

## Resolve the R: target before selecting a cache source

The file URL proves only a Windows drive-letter path. Preserve the historical mapping and classify it before pursuing CSC:

- **Mapped SMB/network share:** recover the UNC target and historical server/share mapping; request the corresponding read-only server-side snapshot or backup. Then assess whether client-side CSC also holds local copies.
- **DFS or another namespace:** preserve the historical namespace/referral mapping and identify the underlying server/share before requesting its snapshot.
- **Local fixed or removable volume:** request a forensic image of that R: volume or original media. CSC is not the relevant source for a local volume.
- **SUBST or another local redirection:** preserve the mapping and image the underlying path/volume.

Do not connect to a live share or rehydrate a historical mapping. The current export contains no UNC target, so this decision must be made from the original profile/machine records or an independently preserved mapping log.

## Hypothesis and gate

First establish from the preserved profile and machine records whether R: was a local volume or a mapped network share. If it mapped to a network share, determine whether Windows Offline Files was enabled and whether the relevant share or folders were cached or marked always available offline.

If, and only if, both conditions are supported, the historical workstation image may contain cached copies of the missing R: files under the CSC Offline Files cache. Microsoft documents the CSC folder as the location where Windows stores Offline Files; the usual location is `%SystemRoot%\CSC`, with a configurable location under `HKLM\SYSTEM\CurrentControlSet\Services\CSC\Parameters`. Offline Files policies are represented under `Software\Policies\Microsoft\Windows\NetCache`; policy can designate files/folders always available offline, and automatic caching may retain a copy when a user opens a file on a share. See:

- [Microsoft: change the CSC folder location](https://learn.microsoft.com/en-us/troubleshoot/windows-client/networking/change-csc-folder-location-with-cachelocation-registry)
- [Microsoft: move the CSC folder](https://learn.microsoft.com/en-us/troubleshoot/windows-client/networking/move-client-side-caching-folder)
- [Microsoft: ADMX Offline Files policy](https://learn.microsoft.com/en-us/windows/client-management/mdm/policy-csp-admx-offlinefiles)

## Historical configuration checks

Preserve and inspect these values in the historical hives, without changing them:

- The user's R: drive mapping and its remote UNC target.
- Computer and user policy under `Software\Policies\Microsoft\Windows\NetCache`: `Enabled`, `AssignedOfflineFiles`, and (for the computer policy) `AlwaysPinSubFolders`. An explicit UNC entry matching the R: share is strong evidence that the share or folder was assigned for offline use.
- `PurgeAtLogoff`: when enabled, Windows deletes local copies of cached offline files at logoff without synchronizing them first. Its presence can explain why a cache is empty.
- `EncryptCache`: if enabled, Offline Files cache contents are encrypted. Preserve the original cache and machine/profile image intact; do not attempt to bypass encryption or acquire credentials.
- `HKLM\SYSTEM\CurrentControlSet\Services\CSC\Parameters\CacheLocation`: the CSC cache may have been moved from the usual location.
- The Offline Files feature policy `Enabled`: Microsoft documents that an unconfigured policy leaves Offline Files enabled by default on Windows client computers, and disabled on Windows Server unless changed by the user. Confirm the historical host type and policy rather than assuming either state.

Microsoft's Windows 11 policy documentation also states that automatic caching can retain a local copy when a user opens a file on an automatic-caching network share, and that AssignedOfflineFiles/AlwaysPinSubFolders can designate files or folders for offline use. This makes the 14 bookmarks useful search targets, while leaving actual cache coverage unproven. See [Microsoft Learn: ADMX Offline Files policy](https://learn.microsoft.com/en-us/windows/client-management/mdm/policy-csp-admx-offlinefiles), especially Pol_Enabled, Pol_AssignedOfflineFiles, Pol_AlwaysPinSubFolders, Pol_EncryptOfflineFiles and Pol_PurgeAtLogoff.

## Acquisition instruction

If the gate is met, acquire the complete historical workstation image and preserve the entire configured CSC tree, CSC database and associated logs, together with the relevant SYSTEM/SOFTWARE and user-profile registry hives. Check the R: mapping and Offline Files policy/configuration before interpreting the cache. Preserve the original cache before any synchronization, purge-at-logoff, reinitialization, migration, or cache rebuild; those operations can remove or change the only surviving local copies.

Prioritize searching for the exact bookmarked paths above, plus the BX25 transfer index and the H-17 ordinary-records index. A cache hit could provide a joint source for K04 (scanner/release or transfer provenance) and K08 (mug-stock, return index, desk/photo-caption material). The bookmarks do not establish that these files were opened, pinned, or cached. The existence of CSC, the historical R: mapping, and cache coverage all remain unproven.

If R: was a local volume, or Offline Files was disabled and no relevant cached copies are present, close this lead. Do not access a live system or reconnect to a share. This is historical evidence preservation only.
