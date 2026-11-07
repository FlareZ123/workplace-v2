# Conditional R: drive Offline Files / CSC retrieval lead

**Status:** source-acquisition hypothesis only. No CSC image, cached file, K04 bytes, or K08 words have been recovered.

## Source clue

The supplied `retired-office-bookmarks.html` contains Windows file URLs under `file:///R:/`, including:

- `R:\Records\INDEX\IR-261003-H17.txt`
- `R:\IT\desk-images\oldscan\scanrelease.txt`
- `R:\Stores\consumables\mug-stock.xls`
- `R:\Stores\returns\SEP26\index.htm`
- `R:\IT\desktop-move-2026.html`

The incident index and the other referenced files are absent from the surviving ZIP. The current acquisition request already calls for the historical R: mapping and a retired workstation image, but does not explicitly name the Windows Client-Side Cache (CSC).

## Hypothesis and gate

First establish from the preserved profile and machine records whether R: was a local volume or a mapped network share. If it mapped to a network share, determine whether Windows Offline Files was enabled and whether the relevant share or folders were cached or marked always available offline.

If, and only if, both conditions are supported, the historical workstation image may contain cached copies of the missing R: files under the CSC Offline Files cache. Microsoft documents the CSC folder as the location where Windows stores Offline Files; the usual location is `%SystemRoot%\CSC`, with a configurable location under `HKLM\SYSTEM\CurrentControlSet\Services\CSC\Parameters`. Offline Files policies are represented under `Software\Policies\Microsoft\Windows\NetCache`; policy can designate files/folders always available offline, and automatic caching may retain a copy when a user opens a file on a share. See:

- [Microsoft: change the CSC folder location](https://learn.microsoft.com/en-us/troubleshoot/windows-client/networking/change-csc-folder-location-with-cachelocation-registry)
- [Microsoft: move the CSC folder](https://learn.microsoft.com/en-us/troubleshoot/windows-client/networking/move-client-side-caching-folder)
- [Microsoft: ADMX Offline Files policy](https://learn.microsoft.com/en-us/windows/client-management/mdm/policy-csp-admx-offlinefiles)

## Acquisition instruction

If the gate is met, acquire the complete historical workstation image and preserve the entire configured CSC tree, CSC database and associated logs, together with the relevant SYSTEM/SOFTWARE and user-profile registry hives. Check the R: mapping and Offline Files policy/configuration before interpreting the cache. Preserve the original cache before any synchronization, purge-at-logoff, reinitialization, migration, or cache rebuild; those operations can remove or change the only surviving local copies.

Prioritize searching for the exact bookmarked paths above, plus the BX25 transfer index and the H-17 ordinary-records index. A cache hit could provide a joint source for K04 (scanner/release or transfer provenance) and K08 (mug-stock, return index, desk/photo-caption material). The bookmarks do not establish that these files were opened, pinned, or cached. The existence of CSC, the historical R: mapping, and cache coverage all remain unproven.

If R: was a local volume, or Offline Files was disabled and no relevant cached copies are present, close this lead. Do not access a live system or reconnect to a share. This is historical evidence preservation only.
