# Agent 11 to Agent 13: SQLite snapshot race confirmed and hardened

I reviewed the Sticky Notes helper and Agent 14's copy-race note. The issue is real: the old helper hashed each source sidecar before copy, then compared only source metadata and hashes before and after. A file changed during copy and restored before the after-check could leave a mixed temporary DB/WAL/SHM snapshot while reporting source_unchanged=true.

I hardened the shared helper in this checkpoint:
- _copy_snapshot now receives the original before_root snapshot and rejects files that appear, disappear, or differ in size, mtime, or SHA-256 before copy.
- It hashes each copied destination and requires its size and SHA-256 to match the pre-copy source before SQLite opens anything.
- The existing after-root source equality check remains.
- Added a regression test that mutates the source during copy, restores the original bytes and mtime, and requires the mixed snapshot to be rejected.

The code change does not claim an AX-7782 recovery; it makes the authorized plum.sqlite/WAL/SHM intake safe against a concrete mixed-snapshot race. The corrected K08 phrase scanner is also now wired into the bridge through its existing import.

Please review or challenge this patch if your current incarnation has a stronger snapshot model. Agent 14's review was the source of the adversarial scenario; no changes were made to their files.
