# AX-7782 temporal eligibility gate for K04/K08

**Status:** source-derived chronology discrepancy; no K04 bytes or K08 phrase recovered. This note narrows the existing [canonical-object joint retrieval lead](h17-ax7782-canonical-object-joint-retrieval-20261107.md).

## Observed timestamps

| Source record | Timestamp | What it says |
|---|---:|---|
| MAIL-13 Date header | 2026-10-02 09:56:00Z | Calls AX-7782 the final custodian handoff / actual retained copy for IR-261003-H17 |
| Selected PS-0417 RECOVER ACK2 | 2026-10-03 18:02:00Z | Selected K04 job payload under recovery-routing.json |
| AX-7782 COMMIT row, receipt_utc | 2026-10-03 20:55:10Z | COMMIT, dry_run=false, 8 chunks, object IR-261003-H17 |
| MAIL-20 Date header | 2026-10-04 11:06:00Z | Says Bundle 06 was staged as a local directory and trimmed to extractable material |

Derived intervals:
- MAIL-13 Date → selected PS-0417 ACK2: **32 h 06 min**.
- PS-0417 ACK2 → AX-7782 receipt_utc: **2 h 53 min 10 s**.
- AX-7782 receipt_utc → MAIL-20: **14 h 10 min 50 s**.

These timestamps are directly present in the source headers/log. The intervals are arithmetic.

## Why this matters

The canonical identifier still joins the K04 ESC-N route, K08 envelope ID (H17-IR-261003), and AX-7782 transfer object (IR-261003-H17). That establishes a common object reference, not the time or contents of the stored snapshot.

There are at least two materially different readings:

1. **MAIL-13 is the actual handoff time.** Then AX-7782 may predate the selected K04 print by 32 h 06 min and cannot contain the selected PS-0417 ACK2 output. It may still be a valid K07 retained transfer or an earlier archive copy.
2. **MAIL-13 is an advance designation/receipt instruction.** Then the 20:55:10Z AX-7782 COMMIT may be the actual snapshot event, 2 h 53 min 10 s after the K04 ACK2, and the payload could contain K04.

The current export does not establish whether MAIL-13 was sent in advance, whether `receipt_utc` is the actual commit time or a later ledger/export timestamp, or whether the transferred object's content version changed between those events. Do not silently resolve this conflict in favour of the more convenient date.

## K07 selection control

The recovery-routing rule for K07 explicitly selects the committed transfer confirmed by the custodian receipt, requires `COMMIT` with `dry_run=false`, then takes the greatest attempt for each sequence 0–7. AX-7782 has attempts 1 and 2 for every sequence. The greatest-attempt checkpoint bytes, in sequence order, are:

```
8947CEDCB9CC73BAB7E87BE63302C5C9
```

SHA-256 of those 16 bytes, truncated to 16 bytes, is:

```
93495F5E425AB8E592123DABAEB68545
```

Hashing that component reproduces the accepted K07 slot commitment. This is a positive control for the checkpoint selector and the retained K07 component. It does **not** prove the AX-7782 chunk payloads are present in the local export or that K04/K08 were included.

## Required falsifiable acquisition

Obtain together:
1. Native MAIL-13 with full headers, thread and any delivery/receipt metadata.
2. Original queue/receipt ledger and event semantics for AX-7782, including the distinction between designation, dispatch, commit, receipt and later export time.
3. AX-7782's original manifest/object metadata, version timestamp, all eight 1 MiB chunk payloads, per-chunk hashes and accepted-attempt records. Preserve attempt 1 as provenance; the current K07 selector chooses attempt 2 for each sequence.
4. Bundle 06 manifest and trim/omission log, to establish whether the selected K04 source and K08 envelope/margin material were included in the object snapshot.

**K04 gate:** only retain AX-7782 as a possible carrier of the selected PS-0417 output if the original object version is demonstrably after 2026-10-03 18:02Z and its manifest/content includes the ESC-N source. If the actual snapshot predates that event, retire AX-7782 as a source of the selected K04 print.

**K08 gate:** even if the object is post-K04, independently establish that Emily's final envelope wording had already been authored and included by the snapshot time. MAIL-20 is post-commit and the supplied note extracts have no authoring timestamps for N23; the current evidence cannot establish this.

MAIL-13 explicitly says its *handoff print* contains only the reference and receipt chain, not the whole archive. Do not mistake that print for the eight-chunk payload.

## Conclusion

AX-7782 remains a high-value **conditional** joint retrieval target because of the canonical object-ID join and the K07 retained-copy selection. The timestamp conflict is a hard eligibility gate: until the original event semantics are recovered, the transfer cannot be asserted to contain the selected K04 object. K08 has a second independent inclusion-time uncertainty. The full AX-7782 object and Bundle 06 manifest/omission log are the decisive records.