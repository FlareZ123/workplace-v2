# H-17 incident archive recovery

**Six of eight REC8/1 components** have passed the unmodified official slot verifier; K04 and K08 remain unresolved, so combined acceptance is **INCOMPLETE**.

| Slot | Verified component | Primary evidence |
|---|---|---|
| K01 | `049AAB2E1CDE7A82CD7C60234303C91A` | signed WN-14, mail 03, 06, 14 |
| K02 | `0D7E3AB56FB75DA3EB0E2E06786D239E` | LT-204 GOOD/HOLD UTC filter, greatest revision per seq |
| K03 | `1384AF96E25D6ADA666209CB55E062FA` | signed PTW-417 CLOSED AS_LEFT, bay B,D,A,C |
| K04 | **missing** | ESC-N printer job PS-261003-0417 has unverified ACK payload |
| K05 | `FF8B78200A56E8586DCDA00EF01E4572` | TRP2 valid CRC, greatest seq per latch |
| K06 | `5DBF40EE52FAAED9A536D3326CF0D95A` | RC-17 revision C, DRAIN/ISOLATE/PURGE/VERIFY |
| K07 | `93495F5E425AB8E592123DABAEB68545` | AX-7782 transfer, greatest retry attempts |
| K08 | **missing** | final keeper caption absent from supplied drafts |

Detailed evidence from both researchers:
- [Initial six-slot recovery status](h17-recovery-status.md) and [K04 three-arbitrary-byte search program](tools/k04_three_byte.c).
- [New K04/K08 evidence including decrypted supplementary PDF provenance](h17-six-pass-and-open-slots.md).
- [Partial accepted candidate](../resources/candidate.json) and [reproducible offline reducer](../resources/work/recover_six.py).

Priority: obtain authentic K04 spool payload bytes and the exact K08 keeper caption, avoiding repeated verification of six solved slots. A SHA-256 commitment verifies guesses but does not reconstruct arbitrary missing material.
