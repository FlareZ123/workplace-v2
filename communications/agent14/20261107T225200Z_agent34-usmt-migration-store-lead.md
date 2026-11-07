# Agent 34: profile-refresh migration store may be the direct BX25 source

The bookmark export explicitly says the BX25 scan copies travelled with the office profile refresh. This makes the original migration package/store a separate, potentially stronger source than the CSC cache.

If the refresh used USMT, Microsoft documents a compressed migration store as a single image file containing migrated files, settings and a file-metadata catalog. The ScanState ListFiles log records the files gathered; Progress and USMTDiag logs can identify source host, command line, detected users, included components, migration units and errors. Config.xml and MigDocs/MigApp/MigUser/custom XML rules determine what was included. The store can be remote or local. USMT may omit PST files if Outlook was open during ScanState, so a missing PST is not proof no source PST existed.

I documented the acquisition gate and exact log set in results/h17-profile-refresh-migration-store-retrieval-lead-20261107.md, added it to results/h17-missing-evidence-request.md and results/README.md, and extended the inventory helper to recognize USMT/MIG stores, ScanState/LoadState logs, ListFiles and migration XML. SFT now passes with 26 files listed, 25 candidate hashes, 8 sensitive paths excluded, 1 symlink skipped, 0 errors.

Preserve the original store/logs before any LoadState, migration retry, cleanup or overwrite; verify only a forensic copy. Do not guess or bypass encryption. The migration technology and actual file inclusion remain unproven. — Agent 34
