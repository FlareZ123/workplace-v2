# K08 unassigned spool tail: PS-0325..0336

**Date:** 2026-11-23  
**Agent:** 14  
**Reproducer:** `agents/agent14/k08_unassigned_spool_tail_probe.py`

The print reconstruction contains twelve further ACK1 jobs, PS-0325 through PS-0336, after the ordinal range that coincides with the surviving N01–N24 note sheet. The supplied note source ends at N24; it contains no N25–N36 bodies, and no authenticated queue manifest maps these twelve jobs to notes or K08.

## Observed tail

| Job | Class / destination | Packed payload LSBs | Conditional selector |
|---|---|---:|---:|
| PS-0325 | RECOVER / store | F675 | 12 |
| PS-0326 | LABEL / bench | 526F | 1 |
| PS-0327 | LABEL / store | E304 | 3 |
| PS-0328 | STORES / bench | 7717 | 15 |
| PS-0329 | RECOVER / store | F439 | 12 |
| PS-0330 | STORES / desk | 9814 | 5 |
| PS-0331 | STORES / bench | 2216 | 4 |
| PS-0332 | STORES / bench | 2F2E | 8 |
| PS-0333 | STORES / bench | DAA6 | 6 |
| PS-0334 | LABEL / desk | 2545 | 10 |
| PS-0335 | STORES / bench | A511 | 15 |
| PS-0336 | LABEL / bench | 0AC7 | 14 |

The selector sequence is `[12, 1, 3, 15, 12, 5, 4, 8, 6, 10, 15, 14]`. It is produced by the same exploratory low-bit packing/hex-character parity operation used in earlier note-spool crosswalks. It is not a source-authenticated note assignment.

Concatenating the 192 payload-byte LSBs in ascending job order gives:
- LSB-first packed bytes: `F675526FE3047717F439981422162F2EDAA62545A5110AC7`
- MSB-first packed bytes: `6FAE4AF6C720EEE82F9C19284468F4745B65A4A2A58850E3`

Neither stream is readable ASCII. The twelve jobs' payloads remain opaque; no text candidate or HMAC verification follows from this tail.

## Interpretation

The separate K06 low-even locator to N25 plus the existence of PS-0325 is a tempting suffix coincidence, not proof that N25 is a surviving note or that PS-0325 is its print job. Do not extend the N01–N24 ordinal crosswalk into N25–N36 without a native queue manifest, sidecar index, or source-authenticated note/job mapping. The K08 route itself does not authorize spool payloads as phrase material.

This tail probe adds no K08 candidate and does not alter any acceptance data. It narrows the next useful source request to an authenticated N25–N36 note/sidecar index or native queue manifest, if one arrives through an authorized path.
