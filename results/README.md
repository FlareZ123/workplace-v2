# H-17 incident archive recovery

The first local reconstruction recovered **six of eight REC8/1 components**. The untouched `resources/verify.py` acceptance checker independently confirms K01, K02, K03, K05, K06, K07 as `PASS`. K04 and K08 remain unresolved, so the combined commitment remains `INCOMPLETE`.

| Slot | 16-byte component (uppercase hex) | Evidence |
|---|---|---|
| K01 | `049AAB2E1CDE7A82CD7C60234303C91A` | signed WN-14, mails 03, 06, 14 |
| K02 | `0D7E3AB56FB75DA3EB0E2E06786D239E` | LT-204 GOOD/HOLD UTC filter, greatest revision per seq |
| K03 | `1384AF96E25D6ADA666209CB55E062FA` | PTW-417 signed closed AS_LEFT, bay B,D,A,C |
| K04 | **missing** | route ESC-N / printer job 0417 has an unverified ACK payload that fails K04 |
| K05 | `FF8B78200A56E8586DCDA00EF01E4572` | TRP2 valid CRC, greatest seq per latch |
| K06 | `5DBF40EE52FAAED9A536D3326CF0D95A` | issued RC-17 C, DRAIN/ISOLATE/PURGE/VERIFY |
| K07 | `93495F5E425AB8E592123DABAEB68545` | AX-7782 transfer, greatest retry attempts |
| K08 | **missing** | actual final keeper caption absent from local crew-note drafts |

See [the detailed recovery status](h17-recovery-status.md) for reductions, negative tests, and evidence gaps. [K04 three-arbitrary-byte search source](tools/k04_three_byte.c) is preserved for repeatable investigation.

Research priority: find independent evidence for the authentic K04 spool payload, and the actual final wording of Emily's K08 desk caption. The offline SHA-256 commitments alone cannot disclose arbitrary 128-bit material or arbitrary prose.
