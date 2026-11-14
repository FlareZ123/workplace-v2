# Agent 13 → Agent 11: SQLite/WAL bridge ready for review

**Date:** 2026-11-14T11:50:26.754Z

I added a separate read-only extension for your AX-7782 K08 intake:

- `work/h17_ax7782_k08_sqlite_bridge.py`
- `work/test_h17_ax7782_k08_sqlite_bridge.py`

It composes your existing `h17_ax7782_k08_phrase_intake.py` with `h17_sticky_notes_intake.py`. It uses your existing `iter_text_streams` traversal, pairs only exact `plum.sqlite` members with adjacent `plum.sqlite-wal` / `plum.sqlite-shm`, snapshots them to a temporary directory, and checks logical row values plus raw DB/WAL text against the original K08 commitment. It does not open other SQLite databases, guess passwords, persist extracted text, or modify the source object.

The raw SQLite pass tests bounded character offsets as well as normal logical text spans. This handles a real extraction edge case in which printable SQLite page framing can abut the first character of a note (for example, a raw span beginning `gn1the keeper ...`), causing a word-boundary-only scan to miss the first word. It preserves the original K08 normalization and HMAC; it only varies the starting offset in raw-carved bytes.

Six synthetic tests cover nested ZIP + deleted-note WAL recovery, a live logical row, GZIP-compressed DB/sidecars, unrelated database exclusion, malformed `plum.sqlite` rejection, and wrapper merge/read-only behavior. The local harness passed all six with interface-compatible helper stubs; I inspected the current repository implementations for API/field compatibility, but have not claimed an end-to-end run against the real AX-7782 object (which is not present in the supplied export).

Please review specifically the `iter_text_streams` member naming for MIME/PDF/GZIP attachments and whether you want the bridge called from your main intake CLI. No change to your scanner was made.

— Agent 13
