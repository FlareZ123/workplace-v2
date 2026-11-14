# Agent 11: SQLite rollback-journal intake and damaged-copy fallback

The Sticky Notes intake helper now snapshots every present SQLite sidecar: `-wal`, `-shm`, and `-journal`, with pre-copy, copied-destination and post-copy integrity checks. It raw-carves the temporary copies before SQLite access and preserves those spans with an explicit `sqlite_error` if the read-only SQLite attempt cannot open/query a damaged or hot-journal copy.

Synthetic tests cover journal copying and recovery from an unreadable DB plus journal. Focused local harnesses pass; the full committed helper suite has not yet been run end-to-end. The custodian acquisition request now explicitly includes the rollback journal.

This is an intake-preservation improvement, not an archive recovery: no original profile DB or AX-7782 object is present, and K04/K08 remain missing. See results/h17-k08-intake-correctness-and-snapshot-hardening-20261114.md.
