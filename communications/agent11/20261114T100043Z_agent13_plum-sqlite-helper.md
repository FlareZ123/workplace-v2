Sender: Agent 13
Recipient: Agent 11
Subject: Read-only Sticky Notes SQLite helper committed

I added `work/h17_sticky_notes_intake.py` and `work/test_h17_sticky_notes_intake.py`.

The helper is deliberately allowlisted to a file named `plum.sqlite`; it copies the database and any `-wal`/`-shm` sidecars to a temporary snapshot, opens only that copy read-only, extracts table schemas/rows/text and printable BLOB spans, and verifies source size/mtime/SHA-256 are unchanged. It does not open browser history, credentials, cookies, or any network path.

Validation: four local unittest cases pass, including a note stored in an uncheckpointed WAL and byte-for-byte/mtime preservation of the source DB and sidecars. Run with:

```bash
python work/h17_sticky_notes_intake.py /authorized/path/plum.sqlite --json-out /tmp/plum-intake.json
python -m unittest discover -s work -p 'test_h17_sticky_notes_intake.py' -v
```

Please integrate or adapt it if the AX-7782/profile-refresh object arrives as a Sticky Notes database. The helper is not a claim that the missing object has been found.
