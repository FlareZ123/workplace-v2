# Joint K04/K08 retrieval lead: canonical IR-261003-H17 object and AX-7782 payload

**Status:** source-defined object-selection and custody lead; the original 8 MiB payload is not present in the supplied export, and no K04/K08 bytes are recovered by this result.

## Canonical object identity

The surviving sources use the same two-part incident/facility identifier in two field orders:
- `archive-labels.ini` identifies the archive object as `IR-261003-H17` and scopes the September ESC-N/ESC-S/WATCH-SPARE printer routes under that object.
- `transfer-audit.jsonl` assigns the eight AX-7782 chunk records and its COMMIT to object `IR-261003-H17`.
- MAIL-13 names the final custodian handoff as AX-7782 for `IR-261003-H17`.
- `recovery-routing.json` gives the K08 envelope ID as `H17-IR-261003`, the same two identifier parts in reverse order.
- The selected K04 route is ESC-N, mapped by `archive-labels.ini` to PS-261003-0417; MAIL-16 identifies ESC-N as the North coupon route and explicitly excludes ESC-S and WATCH-SPARE from K08.

This is a cross-record object-identity join. It is not a byte/word derivation and does not prove that the missing components are contained in the transferred object.

## Which transfer is authoritative

MAIL-13 explicitly identifies AX-7782 as the actual retained copy, AX-7778 as the drill, AX-7781 as the dry run, and AX-7783 as stopped before handoff. It says each chunk was retried once and the second attempt supplies the committed chain, with eight chunks numbered 0 through 7. The transfer audit records a non-dry-run COMMIT for AX-7782 and 1,048,576 bytes per chunk. The local `transfer-audit.jsonl` contains only two-byte checkpoint fields and metadata; it does **not** contain the eight 1 MiB chunk payloads.

MAIL-13 also explicitly limits the handoff print: it contains the reference and receipt chain, not the whole archive. It must not be treated as a substitute for the AX-7782 payload.

## Why this is a joint retrieval target

The selected K04 printer route, the K08 envelope identifier and the committed K07 transfer chain all resolve to the same canonical incident object across independent source records. MAIL-20 says Bundle 06 was trimmed from a local directory and that everyday notes were included with technical material because that was how the folder was kept. The actual AX-7782 object may therefore preserve the complete source bundle or omitted original records needed for K04 and K08.

That possibility is not established by the local export. The actual object may contain only a partial export or receipt chain. Its manifest and contents must decide.

## Targeted retrieval

Request the **original AX-7782 committed object** for `IR-261003-H17`, specifically:
1. All eight original 1 MiB chunk payloads, sequences 0–7, using the accepted second attempt for each sequence as specified by MAIL-13.
2. Original transfer manifest, object metadata, chunk hashes/checksums, per-chunk attempt/receipt records, COMMIT receipt, reassembly instructions and final object hash.
3. Any native object-store, removable-media or transfer-host copy, plus the complete Bundle 06 directory and trim/extraction/omission log.
4. Original source paths and file metadata for every member, including the H17-IR-261003 envelope, the K04 escrow-coupon record or attachment, native mail/desk-note material and any photographs/captions if present.

Preserve the accepted object and each chunk separately before reassembly. Do not substitute the two-byte checkpoint values for payload bytes, do not use AX-7778/AX-7781/AX-7783, and do not mix attempts or sequence order. Hash originals and record custody, acquisition time, source medium and any transformations.

## Falsifiers and limitations

If the original manifest shows AX-7782 contains only a receipt/reference chain, a partial export, or no K04/K08 target-bearing records, retire the joint-payload hypothesis and follow the manifest's actual source pointers. The canonical ID join and COMMIT do not establish object contents. No acceptance values, candidate bytes, masks, nonces or verifiers were changed.

