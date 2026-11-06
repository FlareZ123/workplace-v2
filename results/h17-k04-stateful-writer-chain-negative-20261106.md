# K04 stateful-writer hash-chain pilot (negative)

**Date:** 2026-11-06  
**Owner:** Agent 5  
**Status:** Bounded source-causal hypothesis rejected; no candidate promoted.

## Question

The selected printer job has an earlier acknowledged non-RECOVER record and a later RECOVER ACK. Could the spooler maintain a 16-byte state and derive each subsequent payload from the prior state plus the current record metadata? This would provide a whole-object producer rule and a downstream copy-stage join, rather than inferring only CLASS/DEST labels.

The 0420 job provides a second same-job sequence: an acknowledged STORES record followed by an acknowledged RECOVER record. Its RECOVER ACK2 payload was treated only as a copied whole-object control, consistent with the custodian warning that ACK proves receipt rather than byte correctness.

## Source basis and pins

The test reads only these local records:

- `evidence/print/spool-reconstruction.log`, SHA-256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`
- `evidence/h17-supplemental-office-files/print-fleet-retirement-note.txt`, SHA-256 `10c3a6e46b2c8475fd5fd8333cd8546633bda7ca3eac4e813ac059cd045e3cbf`
- `evidence/archive-labels.ini`, SHA-256 `146fa698f44bc9b9fa7a443d8dc71a2e23ff0f883dabd01512f8ade82d3666ad`

The retirement register joins job 0417 to account FA-17 / L-29/N / H17-POL-17/A3 and job 0420 to ST-09 / L-29/W / STORES/FLT. The archive labels independently join ESC-N to job 0417 and WATCH-SPARE to job 0420.

The spool contains 133 payload records. The first 128 are ACK records, including the earlier 0417 LABEL ACK1 and 0420 STORES ACK1. The final five records contain the selected 0417 REQUESTED1 / RECOVER ACK2 / REQUESTED3 sequence, followed by the 0448 RECOVER ACK1 and 0420 RECOVER ACK2.

## Method

The reproducible harness is `agents/agent5/k04_stateful_writer_chain_sft.py`.

1. **Global previous-record chain:** for each of 127 transitions in the 128-record pre-tail ACK prefix, predict the next 16-byte payload from the previous payload and one of three canonical metadata encodings: job/attempt/state/class/destination; the same fields with timestamp; or the raw source line with PAYLOAD removed.
2. **Same-job previous-ACK transition:** use the earlier ACK payload as state and the current RECOVER record's metadata. Test seven standard 128-bit-output transforms (SHA-256, HMAC-SHA256, MD5, BLAKE2s, and asset-keyed HMAC variants) across four metadata encodings. The 0420 RECOVER ACK2 is the whole-object control. The 0417 ACK2 copied bytes are recorded separately and are not treated as physical truth.
3. Run synthetic transition sanity checks for each transform.

The K04 acceptance digest and mask were deliberately not read or used to select a model. No target hash contact was performed.

## Results

| Test family | Models | Exact result |
|---|---:|---:|
| Global previous-record transitions | 18 | Best model 0 / 127 |
| Same-job previous-ACK transitions | 28 | 0 / 28 matches to the 0420 whole-object control |
| Same-job predictions matching copied 0417 ACK2 | 28 | 0 / 28 |
| Synthetic transition sanity checks | 7 | 7 / 7 deterministic |

No stateful hash-chain candidate was promoted. The test does not support a global previous-payload hash chain or a same-job previous-ACK KDF under the tested source metadata encodings.

## Limits and next step

This closes only the bounded hash-chain family above. It does not rule out a device-specific capture operation, a non-hash state transition, or a producer rule whose required input is absent from the surviving export. Further K04 work should require an independently evidenced transition or a new target-bearing source. Expanding arbitrary hash/encoding permutations would not be justified by this result.
