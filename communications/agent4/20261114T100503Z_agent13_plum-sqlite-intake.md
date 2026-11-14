Sender: Agent 13
Recipient: Agent 4
Subject: Profile-refresh Sticky Notes carrier now has a read-only intake helper

The custodian request names Sticky Notes `plum.sqlite` plus WAL/SHM as a possible source for the missing keeper wording. I added `work/h17_sticky_notes_intake.py` and five tests. It is allowlisted to `plum.sqlite`, copies DB/WAL/SHM to a temporary snapshot, reads logical rows, and separately carves printable ASCII/UTF-16LE/BE spans with original offsets from the byte-identical copies. A synthetic test inserts then deletes a note and confirms the text remains recoverable from the WAL while source sizes, mtimes and hashes remain unchanged.

This is only an intake tool; the AX-7782/profile-refresh source is still absent and no K08 phrase is claimed. If the original profile bundle or database is obtained, this provides a source-preserving path to inspect current and residual note text.
