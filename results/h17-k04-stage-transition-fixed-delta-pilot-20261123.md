# K04 RECOVER-stage fixed-delta pilot

**Date:** 2026-11-23  
**Agent:** 21  
**Question:** Does the spool's event-stage sequence select a simple copy/edit operation that transfers from an intact nonselected job to the selected PS-0417 RECOVER/ACK output?

## Falsifiable hypothesis

The candidate hypothesis was that a RECOVER/ACK payload is produced from the preceding payload by a fixed 16-byte delta: either bytewise XOR with a constant or bytewise addition modulo 256. If this is a printer/serializer stage rule rather than a one-off property, the delta should transfer from the intact nonselected PS-0420 STORES/ACK → RECOVER/ACK sequence to a PS-0417 transition into RECOVER/ACK.

This is deliberately a bounded pilot. PS-0420 is not the same source class as PS-0417, so a class-specific transform remains possible; the test only asks whether one common RECOVER-stage delta explains both.

## Source-selected records

The surviving log gives these same-job sequences:

| Job | Event | Payload |
|---|---|---|
| PS-261003-0417 | LABEL / ACK / attempt 1, 16:45Z | `E1E60D5F6B6DD2225FA6D5A2A63AD932` |
| PS-261003-0417 | RECOVER / REQUESTED / attempt 1, 18:01Z | `CD3E4F216ADB2FB180DA2AA90B33F7A4` |
| PS-261003-0417 | RECOVER / ACK / attempt 2, 18:02Z | `A9A9DC5731A5E2AE879C47215C2559D5` |
| PS-261003-0417 | RECOVER / REQUESTED / attempt 3, 18:03Z | `44D53DFC29D7943A95D89371DA58EC64` |
| PS-261003-0420 | STORES / ACK / attempt 1, 17:00Z | `31C9714DD36DB2677BB9006670A9DFFD` |
| PS-261003-0420 | RECOVER / ACK / attempt 2, 18:25Z | `432475F72A62DB39F3D5693E2C937FA4` |

PS-0417's ACK2 remains the route-selected version; attempt 3 is REQUESTED, not ACK. PS-0420 is used only as an intact nonselected transition control.

## Test and result

For each proposed transition (A \rightarrow B), compute:

- XOR delta: (A \oplus B)
- bytewise additive delta: ((B_i-A_i) \bmod 256)
- 64-bit word additive deltas in both big- and little-endian interpretations.

| Transition | XOR delta | Additive delta mod 256 |
|---|---|---|
| PS-0420 STORES ACK → RECOVER ACK | `72ED04BAF90F695E886C69585C3AA059` | `125B04AA57F529D2781C69D8BCEAA0A7` |
| PS-0417 RECOVER REQUESTED1 → ACK2 | `649793765B7ECD1F07466D885716AE71` | `DC6B8D36C7CAB3FD07C21D7851F26231` |
| PS-0417 LABEL ACK1 → RECOVER ACK2 | `484FD1085AC8308CD83A9283FA1F80E7` | `C8C3CFF8C638108C28F6727FB6EB80A3` |
| PS-0417 RECOVER ACK2 → REQUESTED3 | `ED7CE1AB187276941244D450867DB5B1` | `9B2C61A5F832B28C0E3C4C507E33938F` |

The PS-0420 deltas do not equal either PS-0417 transition delta. The 64-bit word deltas also differ in both endian interpretations. Thus neither a common fixed XOR delta nor a common bytewise/wordwise additive delta transfers from the nonselected control to the selected job.

The route-selected direct candidate is also still invalid: PS-0417 RECOVER/ACK attempt 2 XOR the route mask gives `2CFF149C50E54557228E7DE60B3EB7C9`, whose SHA-256 is `11a7f6064781a6ac7678dc6dd24759af95981c8a927f8da4436515354d34549b`; the unchanged K04 commitment is `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`.

## Adjacent REQUESTED-row alternative

MAIL-16 says the ACK **state field** came from the dispatch log and is not a media-integrity flag. A bounded alternative is therefore that the preceding RECOVER/REQUESTED attempt-1 payload, rather than the ACK2 row's payload, is the media operand acknowledged by the next event. The source sequence (18:01 REQUESTED1 → 18:02 ACK2 → 18:03 REQUESTED3) makes this a testable interpretation, while the later REQUESTED3 remains excluded by MAIL-16's explicit no-ACK warning.

Applying the same route mask directly to each same-job row gives:

| Row interpreted as media operand | Candidate after XOR mask | SHA-256 | K04 match |
|---|---|---|---|
| LABEL / ACK / attempt 1 | `64B0C5940A2D75DBFAB4EF65F121372E` | `3a1e9261869a0fcc61e169ad20a23b514d04b6f994452cdcda7186f1973453a5` | No |
| RECOVER / REQUESTED / attempt 1 | `486887EA0B9B884825C8106E5C2819B8` | `b138a3b90d9cfab0f4994e3a38b354bf205265e2bafa2e29b01444b5dfae14ca` | No |
| RECOVER / ACK / attempt 2 | `2CFF149C50E54557228E7DE60B3EB7C9` | `11a7f6064781a6ac7678dc6dd24759af95981c8a927f8da4436515354d34549b` | No |
| RECOVER / REQUESTED / attempt 3 | `C183F537489733C330CAA9B68D430278` | `02402fd772d7c1dd9c62c90f66cc9b1ace9c593d6cbfa58fee96619fc5abeeaf` | No |

This rejects the direct same-mask interpretation of each retained row as the coupon. It does not establish that ACK2's payload is media data, nor does it authenticate the missing attempt-2 request or rendered coupon.

## Conclusion and limits

This pilot rejects only the stated common fixed-delta copy/edit rule. It does **not** reject every possible class-specific serializer, nor does it authenticate the bytes in the reconstructed ACK row. It produces no K04 component and does not justify changing the route, mask, candidate, or verifier.

A real K04 recovery still needs a source-linked complete-output producer or native PS-0417 spool/rendered-coupon evidence. If a native SPL/SHD pair appears, its association to the application label, attempt 2, RECOVER class, ESC-N route, bench destination and ACK state must be established through a contemporaneous queue/dispatch manifest; same-stem pairing or a literal PS string alone is not enough.
