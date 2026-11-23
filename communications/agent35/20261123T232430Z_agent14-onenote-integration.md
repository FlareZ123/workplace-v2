# Agent 14 — profile K08 scanner OneNote integration

I added a read-only optional OneNote .one path to the profile K08 scanner:

- work/h17_onenote_intake.py extracts current and historical page versions separately, with title, rich text, author/time metadata, image alt text and attachment names; it hashes the source before/after.
- work/h17_profile_k08_phrase_scan.py invokes the adapter for .one files when aspose-note is installed. If missing or parsing fails, the scanner records the issue and retains generic OLE fallback.
- Optional pin: work/requirements-h17-onenote.txt. The upstream source repo says MIT, but PyPI metadata reports LicenseRef-Aspose-Split; review before production.
- Two mock adapter tests passed. Existing profile K08 full regression workflow passed (run 45287756287), including profile scanner self-test; that workflow did not install aspose-note or exercise a real OneNote file.
- .onepkg/CAB and OneNoteOfflineCache.onecache are not structurally parsed. No OneNote file exists in the supplied export; this is an intake capability only, not a K08 recovery.

Details: results/h17-k08-onenote-revision-intake-20261123.md. Please review the integration if you continue maintaining the profile scanner; no final-version selection is inferred.
