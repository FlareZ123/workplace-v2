# K08 print-spool payload commitment control (133 records)

**Date:** 2026-11-19  
**Status:** Completed, source-pinned negative carrier control  
**Owner:** Agent 9

## Question

Could one of the 133 surviving 16-byte print-spool payloads be the K08 HMAC16 component itself, or could a direct hexadecimal/ASCII rendering of a payload be the keeper's final phrase?

The control is intentionally bounded. It does not claim to decode the absent native spool/shadow/rendered print object.

## Method

The reproducer `agents/agent9/k08_spool_payload_commitment_control.py` verifies SHA-256 hashes for:
- `resources/acceptance.json`;
- `resources/evidence/recovery-routing.json`;
- `resources/evidence/print/spool-reconstruction.log`.

It parses all 133 32-hex-character payloads and checks:

1. SHA-256 of each raw 16-byte payload and its reversed-byte view directly against the K08 slot commitment.
2. HMAC-SHA256 under the K08 desk nonce for the normalized forward-hex and reversed-byte-hex strings, retaining the first 16 bytes and comparing their SHA-256 to the K08 commitment.
3. Printable-ASCII decoding where every payload byte is printable, followed by the same normalization/HMAC check.

No arbitrary byte permutations, guessed ciphers, or phrase assembly are used.

## Results

| Measure | Result |
|---|---:|
| Payload records | 133 |
| Unique 16-byte payloads | 133 |
| LABEL / STORES / RECOVER | 52 / 41 / 40 |
| ACK / REQUESTED | 131 / 2 |
| Printable-ASCII payloads | 0 |
| Direct component checks (forward + reversed bytes) | 266 |
| Direct component hits | **0** |
| Unique normalized hex/ASCII candidates | 266 |
| HMAC commitment hits | **0** |

The surviving PS-0323 record is one `RECOVER` / `ACK` / `store` row (attempt 1), payload `1E51EFD2E5CA8F4E1FC8B49297B3D74F`. It does not match the K08 component commitment in either byte order, and its forward/reversed hex renderings do not produce the K08 HMAC commitment.

## Interpretation

The surviving spool payload bytes do not directly contain the K08 HMAC16 component, and their simple hex renderings are not the final phrase under the prescribed K08 HMAC. All 133 payloads are non-printable binary values.

This does **not** rule out the absent native PS-0323 output/shadow/rendered object, a separate desk-copy/photo carrier, or a source-dependent transformation not represented by the surviving 16-byte payload field. The ACK row remains evidence of queue receipt, not proof that the missing native output was preserved.

## Reproduction

Run from the repository root:

```bash
python agents/agent9/k08_spool_payload_commitment_control.py
```

Expected summary: `133 unique payloads / 266 direct checks / 0 direct hits / 266 normalized text candidates / 0 HMAC hits`.
