# K04: internal integrity-code hypothesis on historical printer payloads

**Agent 39, 17 November 2026. 258 complete printer-format hypotheses; no internal checksum match.**

## Causal mechanism

A physical 16-byte printer coupon might contain data bytes and an internal error-detecting checksum. If the retained intact printer packets share a codeword format, a damaged copy of the selected coupon could in principle be repaired by enforcing the original code. This tests a different physical **data object and copy stage** from external cassette-ticket CRC issuer or metadata-to-random-seed hypotheses.

No source asserts that the printer actually embeds an integrity code, so the 132 available unselected printer packets are used as complete original-format calibration. The disputed 18:02 ACK2 is excluded from the format gate.

## Frozen construction

Read the original 133 hexadecimal payloads from `resources/evidence/print/spool-reconstruction.log` (SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`). The unique selected PS-261003-0417 RECOVER ACK attempt2 copied payload is at index129. For each of the other 132 payloads, take every possible contiguous two-byte or four-byte checksum-field offset and both byte orders. Compare the field to the checksum of the remaining payload bytes concatenated in original order.

Six 16-bit codecs are CRC-CCITT initialized at zero or 0xFFFF, ARC, MODBUS, KERMIT and X25. Three four-byte codecs are IEEE CRC32, CRC32C Castagnoli and Adler32. The exact named algorithms, byte views and positions generate 180 + 78 = **258** hypotheses and 34,056 intact-packet comparisons.

Independently check correct CRC algorithm fixtures with ASCII `123456789`. The actual source TRP2 recorder has a *known* 20-byte data / four-byte CRC32 layout; exactly **84 of 88 original recorder records** have valid CRC32, with four corrupt frames preserved in the source. The recorder binary SHA256 is `5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba`. This exercises the same kind of whole-record integrity detection on a genuine positive, rather than a synthetic mock.

## Result

| Family | Geometries | Intact printer comparisons | Matches |
| --- | ---: | ---: | ---: |
| Six CRC16 models, two endian views | 180 | 23,760 | 0 |
| Three CRC32/Adler32 models, two endian views | 78 | 10,296 | 0 |
| **Total** | **258** | **34,056** | **0** |

The selected copied ACK2 also matches none of the 258 declared checksum layouts. Whole-packet XOR-byte parity equals zero for only 2 of 133 packets. The [source-pinned Python reproducer](../agents/agent39/k04_embedded_checksum_source_gate_sft.py) asserts all original source hashes, selection, calibration results, source positives, and no printer CRC match. It does not use the K04 commitment to fit a code and it does not mutate the original archive.

## Implication

**No usable error-correcting redundancy was found within 16-byte printer packets** in these standard contiguous-checksum layouts. This branch provides zero original K04 bits and no complete K04 candidate. It does not rule out nonstandard CRC polynomials, noncontiguous integrity positions, a separate paper/print medium checksum or error-correction outside the 16-byte payload, and a different issuer architecture. Extra arbitrary checksum variants without a source-format witness would be underconstrained. The next useful reconstruction should alter the assumed selected physical object, producer, or stage.

Six original components remain accepted; K04/K08 unresolved and combined REC8/1 INCOMPLETE. Official verifier, acceptance, candidate and evidence files remain unchanged.
