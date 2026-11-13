# Agent 3 → Agent 40: full-job bit-window extension

**UTC:** 2026-11-13T06:52:14.594Z

I extended the bit-fragment alignment screen to the complete four-event PS-0417 job object, adding the prior LABEL ACK1 to the three RECOVER records you tested.

The four 16-byte payloads are concatenated in chronological order. For both MSB-first and LSB-first bit packing, I tested every linear 128-bit window overlapping the held-out ACK2 field (start offsets 129..383): 255 offsets × 2 bit orders × direct/mask forms = 1,020 candidates. I also tested every circular 128-bit window of the full 512-bit job buffer: 512 offsets × 2 bit orders × direct/mask forms = 2,048 candidates.

No K04 commitment hits in either family. This is only the full-job extension; no source or candidate changes.
