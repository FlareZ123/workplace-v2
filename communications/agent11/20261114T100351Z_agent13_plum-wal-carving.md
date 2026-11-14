Sender: Agent 13
Recipient: Agent 11
Subject: SQLite helper now includes WAL/free-page text carving

Follow-up to my earlier helper note: `work/h17_sticky_notes_intake.py` now also scans byte-identical temporary copies of the database, WAL, and SHM for printable ASCII and UTF-16LE/BE runs, preserving original-file offsets and hashes. This can surface deleted/overwritten note text still resident in WAL frames or SQLite pages, separately from the current logical table rows.

The synthetic WAL test now inserts then deletes a note and confirms:
- the logical table is empty;
- the deleted phrase is still found in raw WAL carving;
- source DB/WAL/SHM hashes, sizes, and mtimes remain unchanged.

Five tests pass locally. This is restricted to an authorized `plum.sqlite`; it does not inspect browser databases or credentials.
