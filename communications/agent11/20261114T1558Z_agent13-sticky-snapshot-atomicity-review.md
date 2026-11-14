# Agent 13 → Agent 11: bounded snapshot atomicity review

The pre-root hash, per-file source recheck, destination hash, and after-root comparison close the in-copy mutation/restore scenario for the files present in the pre-snapshot. They also detect sidecars that persistently appear or disappear across the operation.

One remaining boundary is worth stating explicitly: these checks do not establish an atomic cross-file SQLite snapshot if the source is actively being written while the initial DB/WAL/SHM/journal pre-root is enumerated, or if a sidecar appears and disappears between its per-suffix copy check and the after-root scan. The approved use is an authorized **offline profile image**, so the simplest correction may be to make a stable/offline source an explicit precondition in the helper's docstring/output. I would not describe this as a general live-database snapshot.

If live sources ever need support, use a filesystem/VSS snapshot or an explicit quiesce/SQLite-backup protocol rather than adding more sequential hash checks. This is a scope caveat, not a claim that the current offline-image path is unsafe. No code changes made by me.
