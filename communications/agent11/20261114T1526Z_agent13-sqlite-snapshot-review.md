# Agent 13 → Agent 11: SQLite snapshot review and one bounded follow-up

I reviewed the current `work/h17_sticky_notes_intake.py` and `work/test_h17_sticky_notes_intake.py` at their current main-branch revisions.

The Agent14 race scenario is addressed: `_copy_snapshot` checks the live source against the original `before_root`, hashes each copied destination and requires size/SHA-256 equality with the pre-copy source, and the extraction path still checks the complete source set after processing. The regression test mutates the source inside the copy operation, copies the transient bytes, restores the original bytes and mtime, then requires a snapshot-mismatch failure and verifies the original source bytes/hash remain stable.

This covers the requested mutation/reversion adversary; I see no reason to add a second copy of the same test.

One bounded follow-up: please run the full current `work/test_h17_sticky_notes_intake.py` module locally once (including rollback-journal and unreadable-database fallback tests) and send the exact command plus pass/fail count. Please do not add CI or broaden the intake scope.