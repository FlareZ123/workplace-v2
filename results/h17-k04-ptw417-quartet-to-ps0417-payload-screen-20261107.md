# K04 PTW-417 quartet to PS-0417 payload screen

**Date:** 2026-11-07  
**Identity:** Agent 44  
**Status:** bounded negative; no coupon recovered.

## Question

The retained permit export has a same-suffix PTW-390..416 / PS-0390..0416 pattern (27/27). PTW-417 also has a four-bay signed closeout quartet, while PS-0417 contains the selected K04 RECOVER ACK2 event. Does the latest signed/as-left PTW-417 quartet directly produce the PS-0417 16-byte payload under simple identity, digest, keyed-hash or CPython MT seed forms?

## Source-derived inputs

- PTW-417 quartet: latest signed `CLOSED` / `AS_LEFT` revision with an asset in each bay, ordered A/B/C/D: `7DAD0AD4D7DAD6BCBE8E87FD9714519B`.
- Target: `PS-261003-0417`, attempt 2, `ACK`, class `RECOVER`, destination `bench`; payload `A9A9DC5731A5E2AE879C47215C2559D5`.
- The selected payload is kept distinct from attempt 1 `LABEL ACK`, attempt 1 `RECOVER REQUESTED`, and attempt 3 `RECOVER REQUESTED`.

## Bounded test

The SFT tests four explicit quartet orders: A/B/C/D, B/D/A/C (the field-sketch order), D/C/B/A, and C/A/D/B. For each order it compares:

- direct 16-byte identity;
- MD5, SHA-256, SHA3-256, BLAKE2s and BLAKE2b first-16-byte digests;
- HMAC-SHA256 and keyed BLAKE2s using the K04 route mask as key;
- CPython `random.Random` seeded from raw bytes, hex text, big-endian integer and little-endian integer, with `randbytes(16)` output.

Total: **48 comparisons, zero exact matches**.

## Interpretation and limits

This rejects only the stated direct producer family for the source-derived latest PTW-417 quartet and selected PS-0417 payload. It does not falsify a PTW/PS relationship, a different permit revision, a custom firmware transform, a physical copy-stage relationship, or a different source field.

The prior PTW bay-transition donor SFT tested PTW-417 serial blocks through the p951 native-word projection against the K04 commitment; this screen tests a different relation, namely direct production of the PS-0417 payload. The prior PTW-390..416 serial-to-same-suffix screen did not include PTW-417 because its 27 controls were singleton permits. Do not expand this into a generic hash catalogue without new source evidence.

## Evidence integrity

- `seal-receipts.jsonl`: `c00944558636fbcc7e91b81e8e838ffd13fcd5a30d121b41951888766a8a0e32`
- `spool-reconstruction.log`: `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`
- `recovery-routing.json`: `f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5`

Reproduce with `python agents/agent44/ptw417_quartet_to_ps0417_payload_sft.py`. The script asserts the 16-byte quartet and target, 48 comparisons, and zero hits.
