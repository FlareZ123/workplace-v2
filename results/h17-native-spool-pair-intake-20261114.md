# H-17 native SPL/SHD pair intake companion

**Agent 43 | 14 November 2026**

## Purpose

The existing AX-7782 object intake validates the eight-chunk transfer chain and inventories nested containers, but it does not associate native Windows spool payload files with their SHD metadata sidecars. This companion is a read-only intake step for an authorized native spool directory or archive.

## Pairing and evidence rules

The tool is agents/agent43/h17_native_spool_pair_intake.py.

- It pairs SPL and SHD files only when they share the same container, parent path, and normalized filename stem.
- It reports literal job-ID strings found in SHD bytes (ASCII or UTF-16LE) but does not decode undocumented SHD offsets or infer job identity from a filename.
- It searches SPL and SHD members for exact binary and hex-string occurrences of all retained PS-0417 attempts, PS-0300 and the PS-0317/0318/0323 controls, the K04 mask, the K08 nonce, and relevant literal identifiers/terms.
- It reports hashes, sizes, exact offsets, unpaired files, and ambiguous duplicate groups.
- It safely reads directories, ZIP, TAR, and GZIP containers in memory, with path-traversal/symlink checks, nested-depth and member/total-size caps. It does not extract archive members to disk.
- It does not parse spool formats, transform payloads, decrypt content, or promote any candidate.

## Validation

The synthetic self-test creates three correctly scoped pairs (including a nested archive), two unpaired members, and duplicate stems in separate parents. It verifies exact payload and job-ID hits; it passes.

The tool was also run against the supplied h17-archive-dump.zip. It found **zero native SPL/SHD members and zero pairs**. This is consistent with the export containing only the reconstructed text spool log, not native job objects.

## Next source-bearing action

First obtain the bookmarked R:/IT/desktop-move-2026.html calendar and the original workstation profile-refresh/migration package with its manifest/log set; this is the primary acquisition lead and may identify or contain the original BX25 scans and spool directory. If an authorized spool directory or archive is recovered from that package, run the companion against it and preserve the JSON output. Treat the AX-7782 retained object as a separate candidate only after authenticating the original mail namespace, receipt schema, and object-version eligibility. Prioritize PS-0417 attempt-2 and PS-0300, while retaining PS-0317/0318/0323 as controls. A filename pair is only a candidate association; a literal job-ID hit in SHD, matching payload bytes in SPL, and independent queue/dispatch evidence are needed to establish the job mapping.

This tool does not recover K04 or K08 from the current export. The original SPL/SHD objects, queue metadata, rendered output, and physical recovery-envelope/Emily desk-note witnesses remain missing.
