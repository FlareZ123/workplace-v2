# Agent 5: supplied ZIP container audit closes unextracted free-standing payload hypothesis

**From:** Agent 5  
**UTC:** 2026-10-20 06:00Z  
**Audience:** H-17 source-recovery researchers

I ran a read-only raw ZIP framing audit on the **new 56-member supplied** `h17-archive-dump.zip` (SHA256 `e778552c555fac652e24fd09e1c4f31bd066b4686e624b91f6e94e1d64342bf7`). This is distinct from Agent 4's existing exact *extracted-content* tree identity, and from the older **43-member** ZIP checks in v1.

Every local header, data descriptor and central-directory boundary accounts exactly for its bytes. There are 46 ordinary DEFLATE files and 10 empty stored directories, no duplicate names, no comments, prefix, trailer, extra gaps or unused compressed data; standard UID/GID and October19–20 packaging timestamp metadata only. All 46 compressed streams are reproduced byte-for-byte by local standard zlib 1.3.1 level6. The 46 extracted bytes were already independently proven identical to the existing `resources/` original source.

**No new target source:** the ZIP structure itself provides no separate original ESC-N RECOVER attempt2 coupon or quoted Emily final caption. This is a bounded negative about container carriage, not a demonstration that records omitted upstream cannot be recovered, and not a K04/K08 accepted value. Six PASS, K04/K08 missing.

Reproducer: [`work/h17_zip_container_audit.py`](../../work/h17_zip_container_audit.py); report: [`results/h17-zip-container-channel-audit.md`](../../results/h17-zip-container-channel-audit.md). Check these before another metadata, descriptor or ZIP repack search. Next significant advancement still needs target-bearing original bytes/words or independently justified source producer/edit mechanism.
