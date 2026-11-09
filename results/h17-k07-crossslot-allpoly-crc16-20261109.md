# AX-7782 checkpoint-to-REC8 slot CRC16: all-polynomial cross-slot screen

**Agent 17 | 9 November 2026 | original archive and commitments unchanged**

## Complete-candidate architecture under test

The accepted transfer AX-7782 has exactly eight `CHUNK` checkpoints, each exactly two bytes, while REC8/1 comprises eight 16-byte components. A *hypothetical* exporter could have produced each checkpoint by taking a CRC16 of its corresponding component, with an unknown uniform CRC polynomial, common initialization/final XOR, and sequence mapping. If established, two checkpoints could constrain the missing K04/K08 values, though 16 bits alone would not determine either 128-bit component. This is a cross-slot source relation rather than an isolated K04 printer-byte or K08 phrase guess. Neither the route sheet nor the transfer log authenticates the assumed chunk-to-slot correspondence.

Six original 16-byte component values are individually **SHA256 PASS** under unchanged `resources/acceptance.json`. The acknowledged AX-7782 transfer has eight attempt-2 checkpoint bytes, in seq order: `8947 CEDC B9CC 73BA B7E8 7BE6 3302 C5C9`. The original transfer-log SHA256 is `32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf`.

## Exact finite test

Use an arbitrary nonzero 16-bit feedback polynomial tap pattern (65,535 values), a left- or right-shifting bit update, source bytes in normal or reversed order and bits within each byte normal or reflected, any of eight circular slot phases, forward or reverse slot order, and either checkpoint-byte orientation. For all six component messages of the same 16-byte length, any fixed CRC initial state induces a common final displacement and is absorbed into one unknown 16-bit XOR offset. Calibrate this offset from K01; require K02's complete checkpoint to match and then four more independently known complete slot-checkpoint controls K03, K05, K06 and K07. The K01/K02 difference gate permits efficient enumeration of **16,776,960 layouts per source-view combination**, with no cryptographic preimage brute-force.

Also compare the independently reconstructed original pre-reducer inputs instead of the 16-byte digest components for each of K02, K03 and K07, in all eight combinations. Their raw input sources are K02 telemetry's 16-byte selected DIAG_WORD block `E1A5E474BAD7E853A2E8C71D3317D507`, K03's 47-byte joined signed serial string `SG-D7DAD6BC|SG-9714519B|SG-7DAD0AD4|SG-BE8E87FD`, and K07's original 16-byte checkpoint chain. Each raw input's SHA256 first 16 bytes independently reproduces its known accepted component. For variable-length K03, this extension assumes the same *post-CRC* XOR displacement with zero CRC initial state; the arbitrary-CRC-initializer equivalence is assured only when all input lengths are equal.

The fixed six-source search totals **134,215,680 layout presentations** across the eight input-view combinations. Genuine planted original-shaped CRC16 controls, including an unknown common XOR displacement, reversed source byte order, reversed slot assignment, and swapped checkpoint endian, recover the full correct six-point mapping.

## Original-source outcome

| Pre-reducer input choice (K02,K03,K07) | K01/K02 difference gates | Six-source survivors |
| --- | ---: | ---: |
| digest,digest,digest | 230 | **0** |
| digest,digest,raw | 230 | **0** |
| digest,raw,digest | 230 | **0** |
| digest,raw,raw | 230 | **0** |
| raw,digest,digest | 246 | **0** |
| raw,digest,raw | 246 | **0** |
| raw,raw,digest | 246 | **0** |
| raw,raw,raw | 246 | **0** |
| **Total** | **1,904** | **0** |

All genuine historical six-point models fail, even though the synthetic planted mapping is recovered exactly. This excludes the *specified common CRC16 exporter relation*; it does not imply the original eight transfer chunks contain or were derived from REC8 slot values. No target K04 or K08 16-byte candidate is produced, and the 128-bit selected coupon or final caption remains unknown.

**Reproducer:** [Python 3 standard-library original-source SFT](../agents/agent17/k07_crc_poly_crossslot_sft.py), based on pinned `resources/evidence/transfers/transfer-audit.jsonl` and accepted-slot SHA256 gates. The original six other slots remain PASS, K04 and K08 unresolved, combined verifier INCOMPLETE. Do not enlarge this negative into claims about arbitrary packet checksums, arbitrary independent per-slot masks, or original 1MiB chunk payloads.
