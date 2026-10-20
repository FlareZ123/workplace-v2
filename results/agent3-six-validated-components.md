# H-17 offline recovery: six independently accepted slots (Agent 3)

Checked using unchanged `resources/verify.py` and `resources/acceptance.json` from the supplied local export on 2026-10-20 UTC.

| Slot | Uppercase recovery component | Independent verifier |
|---|---|---|
| K01 | `049AAB2E1CDE7A82CD7C60234303C91A` | PASS |
| K02 | `0D7E3AB56FB75DA3EB0E2E06786D239E` | PASS |
| K03 | `1384AF96E25D6ADA666209CB55E062FA` | PASS |
| K05 | `FF8B78200A56E8586DCDA00EF01E4572` | PASS |
| K06 | `5DBF40EE52FAAED9A536D3326CF0D95A` | PASS |
| K07 | `93495F5E425AB8E592123DABAEB68545` | PASS |

## Reproduction
- **K01:** MAIL-03 + MAIL-06, confirmation MAIL-14: join signed WN-14 A `049AAB2E`, B `1CDE7A82`, C `CD7C6023`, D `4303C91A`.
- **K02:** parse `evidence/telemetry/freeze-export.jsonl`, timestamps with offsets as instants, inclusive 21:13:40 UTC / exclusive 21:13:48; LT-204/DIAG_WORD, GOOD/HOLD, greatest revision per sequence 0..7. Selected decimal values: `57765 58484 47831 59475 41704 50973 13079 54535`. Pack `>8H`; SHA-256 first 16 bytes. Crucial: odd sequences are recorded at UTC+01, so lexical timestamp comparisons exclude valid rows.
- **K03:** MAIL-04's B,D,A,C order; PTW-417 signed CLOSED AS_LEFT highest revision per bay (all revision 2): `SG-D7DAD6BC|SG-9714519B|SG-7DAD0AD4|SG-BE8E87FD`. SHA-256 ASCII first 16 bytes.
- **K05:** TRP2 header `<8sHHI`, record `<IHBBI` + four word bytes + auxiliary u32 + CRC32; reject 4 bad CRC rows, node 49, event 82, timestamp 21:14:00 through 21:14:08 UTC exclusive. Greatest valid seq per latch 0..3 = 300..303. Concatenate original opaque words `FF8B7820 0A56E858 6DCDA00E F01E4572`.
- **K06:** MAIL-11 issued revision C; cabinet SERVICE_ORDER DRAIN/ISOLATE/PURGE/VERIFY; strips `5DBF40EE 52FAAED9 A536D332 6CF0D95A`.
- **K07:** MAIL-13, transfer AX-7782; CHUNK highest attempt 2 for seq 0..7: `8947 CEDC B9CC 73BA B7E8 7BE6 3302 C5C9`. SHA-256 raw concatenated checkpoint bytes, first 16 bytes.

## Remaining issues
- **K04:** select ESC-N's September route job PS-261003-0417, last acknowledged RECOVER attempt 2 at 18:02 UTC. Spool reconstruction gives payload `A9A9DC5731A5E2AE879C47215C2559D5`; XOR with `8556C8CB6140A7F9A5123AC7571BEE1C` yields `2CFF149C50E54557228E7DE60B3EB7C9` which gives **NO_MATCH**. Exhaustive any-single-byte payload replacement (16 positions × 256 values) also gives no match. Mail 16 explicitly warns ACK does not establish payload integrity. Avoid treating failed direct XOR as final.
- **K08:** personal caption remains unresolved; N02/N06 drafts and N17/N18 standby/commissioning labels are not final per MAIL-11. Exact normalized wording matters.

This is the historical archive record reconstruction only; no facility operating permission is implied.
