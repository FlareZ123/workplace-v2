# Joint K04/K08 retrieval lead: canonical IR-261003-H17 object and AX-7782 payload

**Status:** source-defined object locator with a hard temporal/content eligibility gate; the original 8 MiB payload is not present in the supplied export, and no K04/K08 bytes are recovered by this result.

## Canonical object identity

The surviving sources use the same two-part incident/facility identifier in two field orders:
- `archive-labels.ini` identifies the archive object as `IR-261003-H17` and scopes the September ESC-N/ESC-S/WATCH-SPARE printer routes under that object.
- `transfer-audit.jsonl` assigns the eight AX-7782 chunk records and its COMMIT to object `IR-261003-H17`.
- MAIL-13 names the final custodian handoff as AX-7782 for `IR-261003-H17`.
- `recovery-routing.json` gives the K08 envelope ID as `H17-IR-261003`, the same two identifier parts in reverse order.
- The selected K04 route is ESC-N, mapped by `archive-labels.ini` to PS-261003-0417; MAIL-16 identifies ESC-N as the North coupon route and explicitly excludes ESC-S and WATCH-SPARE from K08.

This is a cross-record object-identity join. It is not a byte/word derivation and does not prove that the missing components are contained in the transferred object.

## Which transfer is authoritative, and when

MAIL-13 is dated **2026-10-02 09:56Z**. It calls AX-7782 the final custodian handoff / actual retained copy, AX-7778 the drill, AX-7781 the dry run and AX-7783 stopped before handoff. However, the AX-7782 `COMMIT`, `dry_run=false`, `chunks=8` audit row is dated **2026-10-03 20:55:10Z**. MAIL-13 therefore predates the recorded COMMIT by about 35 hours. Treat its wording as an advance designation or receipt instruction unless native mail/ledger evidence explains the discrepancy; it is not contemporaneous proof that the payload had already transferred.

The selected K04 PS-0417 RECOVER ACK2 is dated **2026-10-03 18:02Z**, 2h53m10s before the recorded AX-7782 COMMIT. This makes AX-7782 temporally eligible to contain the selected K04 output only if the audit COMMIT time reflects the actual payload snapshot/version time. If MAIL-13's sent time instead reflects the actual transfer time, AX-7782 predates the K04 job and cannot contain its output. The current sources do not resolve whether `receipt_utc` is the physical commit time, a later ledger/export time, or whether the payload was versioned after the advance mail.

The transfer audit records eight 1 MiB chunk rows and a non-dry-run COMMIT, but the local `transfer-audit.jsonl` contains only two-byte checkpoint fields and metadata; it does **not** contain the eight 1 MiB chunk payloads. MAIL-13 explicitly limits the handoff print to the reference and receipt chain, not the whole archive. The handoff print is not a substitute for the payload.

The selected K07 rule is greatest attempt per sequence; the audit has attempt 2 for all eight sequences. Request attempt-2 payloads as the selected chunks and preserve attempt 1 as provenance/control. The selection rule does not establish chunk contents.

## Why this is a joint retrieval target

The selected K04 printer route, the K08 envelope identifier and the committed K07 transfer chain all resolve to the same canonical incident object across independent source records. MAIL-20 says Bundle 06 was trimmed from a local directory and that everyday notes were included with technical material because that was how the folder was kept. The actual AX-7782 object may therefore preserve the complete source bundle or omitted original records needed for K04 and K08.

That possibility is not established by the local export. The actual object may contain only a partial export or receipt chain. The K08 final-wording authoring time is also unknown: MAIL-20 (2026-10-04 11:06Z) says Bundle 06 was staged as a local directory and trimmed to what could be extracted. Even if the actual AX-7782 snapshot postdates K04 ACK2, the final K08 phrase may have been chosen after that snapshot or omitted from the object. The manifest, object-version timestamp and trim/omission log must decide.

## Targeted retrieval

Request the **original AX-7782 committed object** for `IR-261003-H17`, specifically:
1. All eight original 1 MiB chunk payloads, sequences 0–7, using the accepted second attempt for each sequence as specified by MAIL-13.
2. Original transfer manifest, object metadata, chunk hashes/checksums, per-chunk attempt/receipt records, COMMIT receipt, reassembly instructions and final object hash.
3. Any native object-store, removable-media or transfer-host copy, plus the complete Bundle 06 directory and trim/extraction/omission log.
4. Original source paths and file metadata for every member, including the H17-IR-261003 envelope, the K04 escrow-coupon record or attachment, native mail/desk-note material and any photographs/captions if present.

Preserve the accepted object and each chunk separately before reassembly. Do not substitute the two-byte checkpoint values for payload bytes, do not use AX-7778/AX-7781/AX-7783, and do not mix attempts or sequence order. Hash originals and record custody, acquisition time, source medium and any transformations.

## Falsifiers and limitations

Hard temporal/content gates:
- Obtain native MAIL-13 with full headers/thread, the original queue/receipt ledger with event semantics, and AX-7782 manifest/object-version timestamps. If the actual payload snapshot predates 2026-10-03 18:02Z, retire AX-7782 as a source of the selected K04 print while retaining it as a possible earlier K07/archive copy.
- If the actual snapshot postdates 18:02Z, keep K04 eligible only if the manifest/content includes the ESC-N / PS-0417 source.
- Keep K08 eligible only if the final envelope wording was authored by the snapshot time and is present in the object; if chosen later or omitted, K08 still requires Emily's desk-copy/margin or native thread.
- If the object contains only a receipt/reference chain, a partial export, or no target-bearing records, retire the relevant component path and follow actual manifest pointers.

The canonical ID join is a locator, not proof of content inclusion or temporal eligibility. No acceptance values, candidate bytes, masks, nonces or verifiers were changed.

