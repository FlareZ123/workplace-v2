# Profile-refresh migration store retrieval lead

**Status:** source-acquisition lead only. No migration store, BX25 scan copy, K04 bytes, or K08 words have been recovered.

## Direct source clue

The supplied `retired-office-bookmarks.html` labels itself as an office desktop migration export and says that the BX25 scan copies travelled with the office profile refresh. It also points to the absent R: drive transfer index, scanner release notes, H-17 incident index, mug-stock workbook, September returns index and desktop-move calendar. This is direct evidence that the profile refresh is connected to the missing BX25 material. It does not identify the migration technology or prove which files were copied. Separately, the bookmark description for scanrelease.txt says the old capture terminal stored BX25 folios with a four-position numeric release setting and that its paper key register stayed with the Risk desk. A profile/migration store may preserve an encrypted scan copy or the release-note file; it does not replace the original Risk-desk paper key register or authorize any numeric release setting.

## First discriminator

The first exact file to retrieve is `R:\IT\desktop-move-2026.html`, together with any linked profile-refresh manifest or schedule. It may identify the source/destination host, refresh date, migration product, store location and whether the BX25 scan copies were included. The phrase about BX25 copies appears only in the bookmark export in the surviving local corpus; no independent local source identifies USMT or corroborates the migration method. Keep the migration hypothesis conditional until this calendar or an original migration log is recovered.

## Conditional USMT hypothesis

If the refresh used Microsoft's User State Migration Tool (USMT), the original compressed migration store may contain the files and settings gathered from the source computer. Microsoft documents that a typical compressed migration store is a single image file containing all migrated files, settings and a catalog of file metadata. USMT also supports custom XML migration rules and a Config.xml file that can exclude components. Therefore, a store may contain the BX25 scan copies only if the migration rules and source state included them.

Useful Microsoft references:

- [USMT getting started](https://learn.microsoft.com/en-us/windows/deployment/usmt/getting-started-with-the-user-state-migration-tool)
- [USMT log files](https://learn.microsoft.com/en-us/windows/deployment/usmt/usmt-log-files)
- [Verify the condition of a compressed migration store](https://learn.microsoft.com/en-us/windows/deployment/usmt/verify-the-condition-of-a-compressed-migration-store)
- [ScanState syntax](https://learn.microsoft.com/en-us/windows/deployment/usmt/usmt-scanstate-syntax)

## What the surviving USMT records can prove

- The `ListFiles` log records the files gathered into the store; Microsoft notes it is available only from `ScanState.exe`.
- The progress log can record source/destination computer name, full command line, detected users, whether a profile/component was included, and non-fatal errors.
- `USMTDiag.xml`, when produced, records system/user environment details and migration units with their contents; it can show which custom rules were selected and which files were actually scheduled/stored.
- `ScanState.log` and `LoadState.log` preserve the collection and restore error trail. The XML rule files and `Config.xml` determine what was eligible for migration.
- Microsoft specifically warns that if Outlook is open during ScanState, USMT might not migrate PST files. Therefore, a missing PST in a store is not proof that the source profile had no PST.
- USMT can use a remote store, a local hard-link store, or local/external storage. Do not assume the store sits beside the profile image.

After acquiring and hashing the original, verify a working copy with Microsoft's `UsmtUtils.exe /verify`. If the copy is corrupted, Microsoft's documentation describes `UsmtUtils.exe /extract` as a recovery option for some corrupted stores. Do not run LoadState or a migration retry against the source. If encryption is enabled, use only custodian-provided authorized key material; do not guess or bypass it.

## Acquisition request

Request the original profile-refresh/migration package and its complete manifest/log set, regardless of whether USMT was used. If USMT was used, preserve:

- The original compressed migration store (often a single store image at a configured path; do not assume a filename or extension).
- ScanState.log and LoadState.log.
- Progress log and ListFiles log, if produced. The ListFiles log is particularly valuable because it records the files included in the migration.
- USMT diagnostic log (USMTDiag.xml), if produced.
- Config.xml, MigDocs.xml, MigApp.xml, MigUser.xml, and every custom migration XML file.
- Source/destination host and profile mapping, store path, migration schedule, and any store integrity verification report.
- Any custodian-held store decryption material only if the store is confirmed encrypted; do not guess, brute-force, or attempt to bypass encryption.

Preserve and hash the original store and logs before any LoadState operation, migration retry, cleanup, or overwrite. Do not run ScanState or LoadState against a live system. If the store is encrypted, retain it unchanged and request the authorized key through the records custodian.

## Priority order for the 14 bookmarked paths

When the migration store, CSC cache or original R: volume becomes available, use this source-name-based triage order (a heuristic, not a claim about unseen file contents):

1. **Migration discriminator:** `R:\IT\desktop-move-2026.html` and its linked manifest/schedule, to identify the host, migration method, date and store location.
2. **K04 candidates:** `R:\Risk\Transfers\BX25\transfer-index.htm`, `R:\IT\desk-images\oldscan\scanrelease.txt`, then `R:\Records\INDEX\IR-261003-H17.txt` for the transfer/scan and incident-index chain.
3. **K08 candidates:** `R:\Stores\consumables\mug-stock.xls` and `R:\Stores\returns\SEP26\index.htm`, followed by the ordinary records and profile notes.
4. **Cross-reference:** H-17 renewal ledger, CS-18 loan-set register, EG staff roster and the Finance/PrevERP files.

The complete 14-path list and conditional R: target classification are in [the CSC retrieval lead](h17-r-drive-csc-offline-cache-retrieval-lead-20261107.md). For USMT, the ListFiles log is the preferred discriminator; do not infer inclusion from a bookmark or a filename alone.

## Discriminator

1. Recover the desktop-move calendar and migration manifest/logs.
2. Establish whether the refresh used USMT or another profile migration tool.
3. If USMT was used, inspect the ListFiles log and XML rules for the exact bookmarked R: paths, especially `R:\Risk\Transfers\BX25\transfer-index.htm` and `R:\IT\desk-images\oldscan\scanrelease.txt`.
4. If those paths were included, acquire a forensic copy of the store and extract only from that copy, preserving the catalog and original metadata.
5. If the paths were excluded or absent from the migration manifest, close this route and retain the CSC cache as a separate conditional possibility.

The profile-refresh clue makes this a stronger source lead than a generic search for old files. The migration tool, store location, inclusion rules, encryption state and actual file coverage remain unproven. This is historical record recovery only.
