# H-17 archive ZIP metadata audit (7 November 2026)

## Question

Does the supplied h17-archive-dump.zip preserve original Windows file metadata, an archive-level omission manifest, or hidden ZIP members that could identify the missing Bundle 06 sources?

## Method

Inspected the original uploaded ZIP directly with Python's standard-library zipfile and struct modules. Recorded the archive comment, member count, member names, per-member comments, central-directory DOS timestamps, extra fields, creator platform, compression/flags, external attributes, and archive SHA-256. No source files were modified.

## Findings

- Archive SHA-256: `e778552c555fac652e24fd09e1c4f31bd066b4686e624b91f6e94e1d64342bf7`.
- Archive size: 50,526 bytes.
- 56 central-directory entries: 46 files and 10 directory entries. The 46 file names are the supplied START_HERE, verifier/template, evidence files, 20 email messages, and acceptance data; no additional hidden member was present.
- Archive comment and all per-file comments are empty.
- All 46 files have the same creator platform (Unix, ZIP create_system=3), data-descriptor flag, DEFLATE compression, and external mode `0x81b60000` (Unix regular-file mode 0100664). Directory entries use `0x41ff0000`.
- Every file has only two standard extra-field types:
  - `0x7875`: Info-ZIP Unix UID/GID field, both values zero.
  - `0x5455`: extended modification timestamp.
- No NTFS extra field (`0x000a`), Windows security descriptor, alternate-data-stream record, per-file comment, or original Windows ACL/attribute record is present.
- The extended timestamps form two packaging-time groups: 26 non-mail files at **2026-10-20 04:12:14 UTC**, and the 20 mail files at **2026-10-20 04:12:16 UTC**. The corresponding ZIP DOS fields display 05:12:14/16, consistent with the UTC+1 local clock at packaging time. These are archive-entry timestamps, not the original source-document creation/modification times.
- START_HERE.md states that the preservation reference was prepared on **4 October 2026 11:40 UTC** and that the set is trimmed. The ZIP's uniform 20 October timestamps therefore describe a later packaging operation; they cannot restore the original source-file times.

## Interpretation and limits

The ZIP is a trimmed export package, not a metadata-preserving image of the original Windows mapped-drive folders or office desktops. Its central directory contains no Bundle 06 manifest, omission/deletion list, source-path history, original NTFS timestamps, ACLs, alternate data streams, or file comments. The two-second split between the 20 email files and the other 26 files may reflect packaging order; it does not establish the messages' original file timestamps or a separate source batch.

This does not prove that any particular omitted file existed or survives. It strengthens the case for obtaining the original Bundle 06 manifest/trim log and, if available through an authorized custody path, the original Windows source folders or historical profile image. In particular, the ZIP cannot resolve the bookmarked September return index at R:/Stores/returns/SEP26/index.htm or authenticate an ST-to-PTW/PS crosswalk.

## Reproduction

The key checks can be repeated without third-party packages:

```python
from collections import Counter
from hashlib import sha256
from pathlib import Path
from zipfile import ZipFile

archive = Path("h17-archive-dump.zip")
with ZipFile(archive) as z:
    files = [item for item in z.infolist() if not item.is_dir()]
    print("sha256", sha256(archive.read_bytes()).hexdigest())
    print("entries", len(z.infolist()), "files", len(files))
    print("times", Counter(item.date_time for item in files))
    print("archive_comment", z.comment)
    print("file_comments_empty", all(not item.comment for item in files))
    print("file_extra_fields", sorted({item.extra.hex() for item in files}))
    print("creator_platforms", sorted({item.create_system for item in files}))
    print("flags", sorted({item.flag_bits for item in files}))
    print("compression", sorted({item.compress_type for item in files}))
    print("external_attributes", sorted({hex(item.external_attr) for item in files}))
```

**Conclusion:** no hidden source record or original Windows metadata was recovered from the ZIP container. Preserve the archive hash above as the identity of the supplied export; pursue original Bundle 06 provenance and source files separately.
