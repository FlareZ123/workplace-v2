# K04 late-Z spool cohort: native-source provenance gate

**Date:** 2026-11-07  
**Author:** Agent13  
**Status:** source-provenance gap identified; no new K04 bytes recovered

## Observation from the supplied original export

`evidence/print/spool-reconstruction.log` contains 133 records after its header:

- 128 records run from 07:00 through 17:35 and use `+00:00` timestamps. Each is `ATTEMPT=1 STATE=ACK`.
- Five later records run from 18:01 through 18:25 and use `Z` timestamps. They include `REQUESTED` and `ACK` states and attempts 1, 2, and 3.
- The selected K04 row is the 18:02Z `PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER DEST=bench` record.
- The logical job ID `PS-261003-0417` also appears in the earlier cohort at 16:45 as `CLASS=LABEL ATTEMPT=1 STATE=ACK`.
- `PS-261003-0420` also recurs across the boundary: 17:00 `STORES/ACK/ATTEMPT=1`, then 18:25 `RECOVER/ACK/ATTEMPT=2`.
- `archive-labels.ini` maps the 0417 job to ESC-N. The five-row tail also contains the 0448 and 0420 recovery events.

A raw-byte inspection adds two constraints: all 134 physical lines use LF endings, with no blank line or explicit source marker at the 128/5 transition; and the `Z` suffix used by the five tail records also appears in `evidence/mail/INDEX.md` and the `receipt_utc` fields of `evidence/transfers/transfer-audit.jsonl`. The telemetry freeze uses numeric UTC offsets. Thus `Z` is consistent with a records-office/index serialization convention, while the earlier spool rows retain a different offset form. This may reflect a merge/export-stage boundary rather than a different printer. It cannot identify the producer by itself.

The change in timestamp serialization, state/attempt shape, and reused logical job IDs is an observable cohort boundary. It does **not**, by itself, prove that the rows came from different producers. The log header calls the file a reconstruction from retained fragments, with payload integrity unverified. The custodian note independently says raw acquisition records and spool payloads have not all been validated after extraction, and that ACK proves receipt rather than payload correctness.

## Why the missing source is more specific than "the spool"

The K04 question concerns the provenance of one record in the five-row late-Z tail. The 128-row earlier cohort is not a safe producer control until the tail's source identity is established. The reconstruction may combine:

1. one continuous host spool with a timestamp-format transition;
2. a host spool plus a separate recovery-queue export;
3. a host spool plus printer-local or device-local journal records;
4. another source-to-copy or export-normalization path.

These are hypotheses, not findings. A request for generic host `.SPL/.SHD` files alone may fail to recover the native source that produced the five tail records.

## Falsifiable gate for already-preserved material

If an authorized offline spool/host/device image or retained native export already exists, identify the exact source file, host/device, queue, stable event/job GUID, and record offset for **all five** late-Z rows. Preserve the original export/merge manifest and timestamp/time-zone conversion details. For the selected 0417 row, require:

- exact source event identity beyond the reused logical job name;
- original event time and timezone;
- `ATTEMPT=2`, `STATE=ACK`, `CLASS=RECOVER`, `DEST=bench`;
- independently preserved payload bytes and any source checksum/receipt;
- a source mapping that ties the record to the incident-date ESC-N route.

Use the 16:45 LABEL event and 17:00 STORES event as same-name collision controls. If source metadata proves one continuous queue and a single producer across both timestamp forms, close the separate-source hypothesis. If the tail comes from a distinct queue/device/export, treat that source as the relevant K04 producer and do not train its payload model on the earlier 128 records. If no native source or merge manifest is already preserved, record the provenance gap and stop cross-cohort producer fitting.

## Prior-art and novelty boundary

The 128/5 cohort split, timestamp suffix distinction, reused 0417/0420 job IDs, and MAIL-16 future-request chronology were already documented in v1's [spool cohort identity audit](https://github.com/FlareZ123/workplace-v1/blob/main/results/h17-spool-cohort-identity-audit.md) and [source-rule consistency analysis](https://github.com/FlareZ123/workplace-v1/blob/main/results/h17-source-rule-consistency.md), as well as later v2 agent memories. This report does **not** claim those observations as new. The additional local byte check here found uniform LF endings and no explicit line delimiter at the boundary; the cross-file `Z` comparison is a serialization context check, not a producer discriminator. The contribution is a concise v2 acquisition/validation gate that keeps the already-known source ambiguity visible. No new target-bearing source or K04 bit was found.

## Boundary

This is an internal provenance gate for existing preserved material. It does not reopen the closed custodian channel and authorizes no live printer access, device power-on, remote administration, or print operations. It does not change the K04 selector or the six accepted components. K04 remains unverified.
