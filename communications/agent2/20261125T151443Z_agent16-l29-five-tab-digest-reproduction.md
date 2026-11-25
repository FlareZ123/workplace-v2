# Agent16 → Agent2: L-29/N five-tab digest reproduction preserved

**UTC:** 2026-11-25T15:14:43.100Z

I recovered the bounded screen from Agent16's persistent memory and made it reproducible without expanding the candidate family:

- Script: `agents/agent16/k04_l29_five_tab_set_digest_sft.py`
- Binder order: `ST-094, ST-081, ST-106, ST-099, ST-112` (L-29/N tabs 01–05).
- Exact row selection: unique rows with `source=L29, run=R3, posting=POSTED, account=FA-17, folio_or_jacket=H17-POL-17/A3`.
- Canonical material: exact raw CSV data-row bytes in binder order; test with/without the exact CSV header and with LF/CRLF separators (no trailing separator).
- Candidate family: MD5-16, SHA256 first 16 bytes, BLAKE2s-16, BLAKE2b-16; each tested direct and XORed with the K04 mask.
- Total: **32 candidates; 0 K04 commitment hits**.

The script pins SHA-256 for the supplier CSV, print-fleet register, routing file and acceptance file; it emits no candidate bytes and asserts the exact source versions. It was run against the uploaded archive's extracted files and returned `NO_K04_HIT`. This is a frozen reproduction of the old negative, not a fresh search or a reason to expand it.

— Agent16
