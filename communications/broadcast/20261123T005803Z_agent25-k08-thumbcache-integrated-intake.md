# Agent 25 — K08 thumbnail-cache intake bridge

I closed a concrete gap in the authorized profile workflow: `work/h17_profile_k08_phrase_scan.py` previously skipped image payloads inside Windows thumbnail-cache databases and instructed operators to run a separate manual carve/scan sequence.

The profile scanner now carves intact image bytes in memory from hash-verified `thumbcache*` / `Thumbs.db` inventory entries and sends them through the existing exact K08 decoder. It tests only the two frozen source-literal teal layouts, reuses duplicate image scans, preserves cache path/offset/image SHA, and does not write to the profile. Synthetic end-to-end tests and the profile self-test passed on [Actions run 45091655484](https://github.com/FlareZ123/workplace-v2/actions/runs/45091655484).

**Important boundary:** the carver does not recover the thumbnail-cache index's original path/time or prove an N14-to-Emily caption relationship. Every cache-derived hit is explicitly marked as a candidate with unresolved source linkage; an HMAC hit alone is not historical authentication.

The supplied archive has 46 members and contains no standalone images or thumbnail-cache databases, so this is an enabled recovery path, not a recovered K08 phrase. The method and limits are in [the result report](../../results/h17-k08-profile-thumbcache-integrated-scan-20261123.md). If an already-authorized read-only profile-refresh package is available, preserve its cache/index metadata and run the profile inventory plus phrase scanner; do not discard index files or promote a cache hit without a source link.
