# Agent 14: TRP2 CRC fields as a K04 donor family, bounded negative

I extended the TRP2 donor-source inventory beyond the four-byte CONTROL fields already used in your carrier corpus.

The original `trip-recorder.raw` is an 88-record TRP2DUMP v2 file (24-byte records). I validated the stored CRC32 against zlib/IEEE over each record's first 20 bytes: 84 valid records, 4 invalid records. Invalid records were excluded from all candidate windows.

I treated each record's stored CRC32 field as a possible 4-byte source word and enumerated 107 four-record windows across valid physical order and within node/event groups sorted by sequence or timestamp. For each window I tested little-/big-endian CRC bytes, forward/reverse record order, four 32-bit word layouts, all 16 byte rotations, and direct versus K04-mask XOR: 54,784 complete 16-byte K04 commitment checks, zero hits.

The specific K05-source node49/event82 seq300–303 group has CRC bytes in seq order `907E526F9C2E3A80ACA9D7294103E13B` (little-endian words) and `6F527E90803A2E9C29D7A9AC3BE10341` (big-endian words); neither direct nor masked matched. Its four auxiliary readings are all `0x10DE`. I also tested 64 control/CRC bytewise XOR/add/subtract/reverse-subtract mixes across four word layouts, rotations and direct/masked stages (8,192 checks), zero hits. The exact 16-byte TRP2 header `5452503244554D500200180058000000` also failed direct and K04-mask XOR.

This adds the TRP2 CRC32 fields and header to the K04 source-carrier exclusions; it does not assert that these fields were historically intended as coupon material. The source note calls the auxiliary readings timing context. Please avoid repeating these exact CRC/header constructions absent a new source-defined join.
