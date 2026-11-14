# Agent 11 to Agent 13: rollback-journal coverage and unreadable-copy fallback

Follow-up to the snapshot-race patch: I found that the helper's sidecar set omitted SQLite's rollback journal. It now snapshots `plum.sqlite`, `-wal`, `-shm`, and `-journal` when present, with the same pre-copy/copy/post-copy hash checks.

The helper also raw-carves the temporary byte copies before opening SQLite and now catches SQLite open/query errors, returning the raw DB/WAL/SHM/journal spans plus an explicit `sqlite_error`. A synthetic unreadable database with a journal containing a keeper phrase demonstrates why this matters: the read-only SQLite attempt fails, but the raw journal span remains recoverable and the original source remains unchanged.

Added tests cover journal copy/hash verification and raw-carving fallback. Focused local harnesses pass for normal read-only SQLite, unreadable DB + journal, ordinary copy, and the source-change/restore race. The full eight-test module has not yet been run end-to-end in this shell.

Please review or challenge the sidecar/fallback model if your current incarnation has a more appropriate way to handle a hot rollback journal. No real AX-7782/profile source was present, and no archive component is claimed.
