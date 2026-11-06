# K04 AX-7782 transfer-checkpoint vector: bounded negative and missing queue metadata

**Date:** 2026-11-06  
**Identity:** Agent 26  
**Status:** no K04 hit; a specific original queue export is missing

## Source relationship

The transfer queue note identifies the actual retained copy as AX-7782 for object IR-261003-H17. It distinguishes AX-7778 (pre-incident drill export), AX-7781 (dry run), and AX-7783 (stopped before handoff). It explicitly says the queue's `mode`, `purpose`, and `dry_run` fields are needed to select the actual handoff, and that each checkpoint is a 2-byte opaque field.

The supplied `transfer-audit.jsonl` contains 16 AX-7782 CHUNK records: eight sequence numbers (0–7), each with attempts 1 and 2, each record carrying a 2-byte checkpoint and a 1 MiB byte count. Its AX-7782 COMMIT record contains `dry_run:false`, object IR-261003-H17, eight chunks, and receipt time. However, it has no `mode` or `purpose` fields. AX-7778 also has `dry_run:false`, so that field alone cannot distinguish the actual handoff. The local `evidence/transfers/` directory contains only `queue-note.txt` and `transfer-audit.jsonl`; the queue export itself is absent.

## Bounded checkpoint-vector test

Hypothesis: one 2-byte checkpoint from each AX-7782 sequence forms a 16-byte K04 coupon or component.

Tested:
- all 256 per-sequence choices between attempt 1 and attempt 2;
- checkpoints in sequence order and reverse sequence order;
- each 2-byte field as written and with its two bytes reversed;
- both candidate roles: checkpoint vector as coupon (XOR the route mask, then SHA-256) and as component (direct SHA-256).

This gives **2,048 direct assignments**. No candidate matched the K04 commitment.

A second bounded set tested per-sequence attempt-pair XOR, addition and subtraction modulo 65,536 (both subtraction directions), plus 256 hybrid-byte selections taking one byte from each attempt. These were checked in both byte orders, both sequence directions, and both coupon/component roles: **1,056 additional variants**, also with no hit.

The test preserves the queue note's warning: checkpoint values were treated as opaque bytes, not reinterpreted as chunk sizes or frame counters. No K04 bytes were recovered.

## Evidence and limitations

- `queue-note.txt` SHA-256: `2040af92096bd270352a7c5e4a587ae3a0a26485c2c2a10240ce8504465c788f`.
- `transfer-audit.jsonl` SHA-256: `32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf`.
- The queue note and MAIL-13 identify AX-7782 as the actual retained transfer. The audit's COMMIT fields alone do not establish that selection, and the audit does not say which per-chunk attempt was accepted.
- This negative rejects only the tested direct checkpoint-vector and simple pairwise constructions. It does not establish that the checkpoint fields are related to K04 at all.

## Specific source request

Request the preserved historical transfer-queue export or queue-entry record for AX-7782 / IR-261003-H17, including:
1. the original `mode`, `purpose`, and `dry_run` fields referenced by the queue note;
2. the per-sequence accepted attempt or other selection rule for the eight checkpoint pairs;
3. the checkpoint field serialization/interpretation specification and any receipt/coupon association;
4. original queue ordering and provenance metadata.

This is an offline records-custody request. It does not authorize live transfer-system access. The missing queue export is a concrete source dependency; its existence and contents are not established by the current export.
