# Agent 5: H-17 uploaded ZIP container-channel check (20 October 2026)

## Target-specific question
Does the newly supplied 50,526-byte `h17-archive-dump.zip` contain a second original K04 coupon, K08 caption or other unextracted payload in ZIP comments, duplicate names, file extra fields, gaps, orphan trailer bytes or compressed-data trailing bytes? Agent 4 had already proved that all **46 extracted file contents** match the repository original bytes; this audit checks the **ZIP container**, a distinct input layer.

## Read-only method
Parsed the supplied ZIP's raw local headers in physical offset order, independently decoded the member payload streams, matched compressed streams to Python `zipfile` file contents, checked data descriptors, parsed the central directory, validated the terminal end-of-central-directory record and accounted for every byte boundary. Inspected local and central extra-field tags, comments and duplicate-name inventory. No source or verifier mutation. Portable reproducer: `work/h17_zip_container_audit.py`, accepts a locally held ZIP path.

Source ZIP SHA-256: `e778552c555fac652e24fd09e1c4f31bd066b4686e624b91f6e94e1d64342bf7`.

Observed:
- **56 members:** 46 deflated files and 10 empty stored directories. No duplicate paths.
- **46 standard 16-byte data descriptors**, each CRC and compressed/uncompressed size matching its member. All deflated streams terminate exactly at their declared compressed boundaries; no unused compressed trailing data. **All 46 compressed streams were reproduced byte-for-byte with standard zlib 1.3.1 raw-DEFLATE at level 6**, an implementation-specific positive match.
- **112 local extra fields:** exactly one ordinary Unix UID/GID field (`0x7875`) and one extended timestamp field (`0x5455`) per member. The UID/GID values are zero. The local timestamp field records ordinary mtime/atime/ctime and the central directory contains the corresponding abbreviated mtime. On the 46 files, all local-header creation/change timestamps are the *same* `2026-10-19T20:09:30Z`; mtimes are `2026-10-20T04:12:14Z` for 26 files or `04:12:16Z` for 20 email files. The atimes are four nearby packaging-time values, including one `04:12:34Z` reading on `START_HERE.md`. These highly clustered values are packaging/filesystem metadata, **not an incident-time authentication witness**. Directory timestamp conventions differ from regular files.
- **No ZIP archive comment, member comments, prefixed bytes, end trailer, unexplained between-member gaps, or unexplained central-directory bytes.** Raw ZIP framing accounts for all 50,526 bytes. `zipfile.testzip()` passed CRC for all members.

## Meaning and limits
There is **no hidden free-standing content** in these ZIP container channels to provide an independent original ESC-N RECOVER attempt-2 payload or Emily's final literal caption. This closes a *specific potential source-location hypothesis*, not the overall archive puzzle. Legitimate timestamps/headers are additional metadata, and this check cannot rule out steganography inside valid file contents, compressed bitstreams or original records lost upstream. It also cannot validate authenticity of a corrupted printer payload. Because all 46 extracted file contents were already attested equal by Agent 4, there is no newly observed selected K04 bit or final K08 word from this check.

**Acceptance status unchanged:** K01/K02/K03/K05/K06/K07 PASS; K04/K08 unresolved; combined INCOMPLETE. Direct source-specific custodian intake remains Issue #1.
