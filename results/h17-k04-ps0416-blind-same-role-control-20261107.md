# PS-0416 as a candidate blind same-role control for K04

**Status:** new source-specific acquisition lead; no K04 bytes recovered. PS-0416 is a *conditional* control, not yet proven to use ESC-N or the same physical copy path.

## Why this object is worth retrieving

The surviving spool reconstruction contains a complete single-attempt job immediately before the selected PS-0417 event:

- PS-261003-0416 at 2026-10-03 16:40Z: `ATTEMPT=1 STATE=ACK CLASS=RECOVER DEST=bench`, payload `F1F5A127EA44F563935C63F8A59A2801`.
- The selected PS-261003-0417 event at 18:02Z is also `STATE=ACK CLASS=RECOVER DEST=bench`; it is attempt 2 after a RECOVER REQUESTED attempt and a prior LABEL ACK.
- The local PTW-416 receipt is bay D, revision 1, CLOSED, AS_LEFT, signed, serial `SG-0C814A5E`.
- The North L-29/N return register lists ST-112 as tab 05, "catch, clean". Under the *unverified* +304 ST↔PTW↔PS offset hypothesis, ST-112 maps to PTW-416 / PS-0416. The competing +300 offset does not make that same mapping.

The exact source-to-route join remains unproven: `archive-labels.ini` explicitly maps ESC-N to PS-0417, not PS-0416. The +304 mapping is a candidate inferred from ticket/bay/class relationships, not an authenticated ticket pair. This is why the original route/queue manifest is part of the request.

## Proposed blind control

Retrieve the following together, preserving originals and provenance:

1. The native PS-0416 queue/job record, including logical printer route, job class, destination, attempt history, ACK selector, driver/firmware version and any retry/copy-stage metadata.
2. The complete physical PS-0416 output or retained coupon, front/back, with any sleeve, carbon, ribbon, scan or independent checksum.
3. The original North L-29/N ST-112 binder page, all attachments/underlays, and the PTW-416 permit/serial page. Authenticate whether ST-112 actually identifies PS-0416 and the ESC-N/L-29/N route.
4. Any custody/return record connecting the job, cassette, physical output and retained copy.

Before revealing the reconstructed PS-0416 payload or selected attempt to the analyst, use the independent original record to select the historical object. Then compare the complete physical/copy value byte-for-byte with the withheld reconstruction:

- **Exact 16-byte match:** validates the reconstruction/copy path for this independently selected RECOVER/ACK control, subject to same-route confirmation.
- **Mismatch:** localizes a real copy-stage, serialization or reconstruction discrepancy and gives a blind calibration target.
- **No independent physical value or no authenticated route match:** retire PS-0416 as a same-role control; do not promote its spool payload to truth.

Only after a blind control pass should the same source-defined selector/copy mechanism be applied to PS-0417 ACK2. Do not tune the mechanism against the K04 commitment, the A9A9 prefix, or the selected PS-0417 bytes.

## Evidence boundary

The local spool file is explicitly a reconstruction with payload integrity unverified. Dispatcher ACK establishes dispatch status, not that the recorded 16 bytes equal the physical print. PTW-416 is a maintenance permit, not itself a print witness. The physical print, original job manifest and authenticated ST-112↔PTW-416↔PS-0416 relation are all absent from the supplied export.

Source hashes (supplied ZIP members):

- `spool-reconstruction.log`: `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`
- `archive-labels.ini`: `146fa698f44bc9b9fa7a443d8dc71a2e23ff0f883dabd01512f8ade82d3666ad`
- `seal-receipts.jsonl`: `c00944558636fbcc7e91b81e8e838ffd13fcd5a30d121b41951888766a8a0e32`
- `print-fleet-retirement-note.txt`: `10c3a6e46b2c8475fd5fd8333cd8546633bda7ca3eac4e813ac059cd045e3cbf`
- `supplier-reconciliation-L29.csv`: `73b85da6d358cfc57dd340c1d6b84a5434d50693c6b12b256238ef3ff8c5c87e`

This is a retrieval and blind-validation path, not a new K04 candidate or an assertion that PS-0416 is the selected ESC-N source.
