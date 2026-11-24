# Separate profile-refresh: conditional USMT migration-store intake lead

**Status:** conditional acquisition hypothesis; no AX-7782 bytes or USMT store recovered.

## Question

Could a separately preserved office profile-refresh package be a Windows User State Migration Tool (USMT) compressed migration store? If so, it may contain the missing mug-stock.xls, profile-refresh records, and photo/caption material. AX-7782 is a distinct, high-priority retained object; its format is unknown, and no surviving source joins it to the profile-refresh package. Do not conflate the two acquisition targets.

## Source basis

- resources/evidence/mail/13.eml identifies AX-7782 as the actual retained copy for IR-261003-H17, distinguishes it from AX-7778/AX-7781/AX-7783, and describes eight 1 MiB chunks with retry checkpoints. It does **not** identify the container format.
- resources/evidence/h17-supplemental-office-files/retired-office-bookmarks.html is a cached browser-favorites export from the retiring office profile. It includes:
  - R:/IT/desktop-move-2026.html (profile-replacement calendar);
  - R:/Stores/consumables/mug-stock.xls (tea-room stock sheets);
  - R:/Risk/Transfers/BX25/transfer-index.htm, with the explicit note that BX25 scan copies travelled with the office profile refresh;
  - R:/IT/desk-images/oldscan/scanrelease.txt, with the old capture terminal's release-setting and Risk-desk paper-key-register note;
  - R:/Records/INDEX/IR-261003-H17.txt.
- work/h17_profile_inventory.py already classifies .mig as windows_usmt_migration_store and recursively inventories files, but does not validate/extract a USMT store.
- work/h17_ax7782_object_intake.py handles ZIP/TAR/PDF/SQLite/OLE/image content but does not handle USMT stores.

These records make a separate profile-refresh container plausible; they do not prove that AX-7782 contains it, that either target is a USMT store, or that either contains the missing files.

## External format support

Microsoft describes a compressed USMT migration store as a single image file containing migrated files, settings, and a catalog. The supported utility path is UsmtUtils.exe /verify (including /verify:all) and, when authorized, UsmtUtils.exe /extract to a separate destination:

- Verify the condition of a compressed migration store: https://learn.microsoft.com/en-us/windows/deployment/usmt/verify-the-condition-of-a-compressed-migration-store
- Extract files from a compressed migration store: https://learn.microsoft.com/en-us/windows/deployment/usmt/extract-files-from-a-compressed-migration-store
- USMT how-to: https://learn.microsoft.com/en-us/windows/deployment/usmt/usmt-how-to

## Reusable intake tool

Added work/h17_usmt_store_intake.py with tests in work/test_h17_usmt_store_intake.py.

The helper:
- delegates validation and extraction to the matching Windows ADK UsmtUtils.exe;
- defaults to /verify:all;
- supports selective extraction of the H-17-relevant workbook, profile, text, image, and SQLite file patterns;
- requires a new/empty output directory;
- hashes the primary store plus adjacent .mig/.migNN segments before and after, and hashes extracted files;
- preserves the native USMT log separately from the runner log;
- accepts an authorized decryption key **file**, never a plaintext key argument;
- never invokes LoadState and never writes to the source store.

Eight local unit tests pass against a fake UsmtUtils executable. This validates command construction, output safety, logging, and hashing only; it does not validate a real USMT store or Windows ADK behavior.

Run them from the repository root with: `PYTHONPATH=work python -m unittest -v work.test_h17_usmt_store_intake`.

Example on a Windows system with the matching ADK installed:

~~~powershell
python work\h17_usmt_store_intake.py AX-7782.mig --tool "C:\Program Files\Windows Kits\10\Assessment and Deployment Kit\User State Migration Tool\amd64\UsmtUtils.exe" --out C:\H17-intake\verify
~~~

If verification confirms a store and extraction is authorized, use a new output directory:

~~~powershell
python work\h17_usmt_store_intake.py AX-7782.mig --tool "C:\Program Files\Windows Kits\10\Assessment and Deployment Kit\User State Migration Tool\amd64\UsmtUtils.exe" --mode extract --out C:\H17-intake\extract
~~~

The default extraction allowlist includes mug-stock.xls, desktop-move-2026.html, scanrelease.txt, IR-261003-H17.txt, transfer-index.htm, common Office/document/image formats (including standalone .emf caption files), SQLite databases and their WAL/SHM sidecars. Repeated --include values replace (rather than extend) this default list, so specify every desired pattern when adding spool members. Supply an independently authorized --keyfile only if the store is encrypted; do not assume any unrelated PDF-derived password is the USMT key.

## Next action and limits

If an authorized AX-7782 object or a separately preserved profile-refresh package becomes available:

1. Preserve and hash the original object and its eight chunk reconstruction.
2. Identify the actual container format for that specific object; do not assume .mig or assume AX-7782 and the profile-refresh package are the same object.
3. If UsmtUtils /verify:all accepts it, preserve the verification log and extract only to a new isolated directory.
4. Feed any recovered mug-stock.xls to the existing BIFF/M10 intake and photos/sidecars to the K08 phrase intake. If a native spool directory is independently identified within the acquired package, use the existing read-only SPL/SHD pairer and require SHD/job-ID plus queue/dispatch binding before treating it as PS-0417.
5. If a separate profile image contains Windows/CSC, inspect the CSC namespace tree read-only first; ESE parsing is a fallback for metadata, not the first content-recovery step.

No source bytes were available in the supplied ZIP or inspected repository at the time of this work. No K04/K08 component, source file, or recovery key has been recovered by this hypothesis.
