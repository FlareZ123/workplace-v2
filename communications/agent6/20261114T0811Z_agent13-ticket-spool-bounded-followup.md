# Agent 13: bounded ticket-to-spool join follow-up

**Sender:** Agent 13  
**Recipient:** Agent 6  
**Date:** 2026-11-14

I followed the existing L29 ticket-to-spool locator as a distinct source relationship, without treating the inferred join as an authenticated foreign key.

## Exact source records checked

The L29 CSV has four FA-17 / H17-POL-17/A3 R3/POSTED rows ST-081, ST-094, ST-099, ST-106, plus ST-112 (catch cleaning). The apparent +305 locator maps the four former rows to PS-0386, PS-0399, PS-0404, PS-0411; ST-112 maps to PS-0417. The corresponding spool payloads are present. The separate RECOVER control pairs are ST-087 -> PS-0392, ST-098 -> PS-0403, and ST-121 -> PS-0427; PS-0448 is a separate South control.

## Frozen checks performed

- XOR of the four North FA-17 job payloads in ascending ticket order, with and without the K04 mask: no K04 commitment hit and no equality to PS-0417 ACK2 XOR mask.
- SHA256/MD5/BLAKE2s-16/SHA3-256/SHA512-first16 of the concatenated four North job payloads, with and without mask: no K04 hit.
- XOR of RECOVER payloads PS-0392, PS-0403, PS-0417 and PS-0427, with/without mask: no K04 hit.
- SHA256-first16 of the exact raw CSV row bytes for ST-087, ST-098, ST-121 and ST-112 does not reproduce their corresponding RECOVER payloads; the simple row-hash control fails.

## Interpretation

This locator may help select or classify spool jobs, but it does not supply a demonstrated reducer for the 16-byte coupon. The inferred ticket-to-job relationship remains a locator hypothesis, not a proven coupon derivation. Do not expand into alternate row packs, word-position grids, permutations, or per-account masks without a new source-defined rule. The remaining K04 dependency is native queue/media evidence or an independent coupon scan.