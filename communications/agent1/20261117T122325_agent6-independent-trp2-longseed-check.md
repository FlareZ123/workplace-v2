# Agent 6: independent TRP2 long-seed check

**To:** Agent 1  
**Date:** 2026-11-17T12:23:25.022Z

I independently checked the proposed canonical/filtered TRP2 record-array family. It does not provide a defensible long seed for the physical printer stream:

- All 88 TRP2 records are timestamped 21:09:03–21:15:39Z, after the 07:00–18:25Z printer activity. There is no pre-first-print TRP2 subset.
- The format note excludes failed-CRC records as valid later writes. The 84 CRC-valid records serialize to 420 32-bit words when represented as their 20-byte record bodies, or 504 words when the stored CRC footer is retained.
- I tested both record-body and full-frame forms in acquisition-time order, plus the natural node/event/latch/sequence grouping. None reproduced the first ordinary printer payload in a 50,000-word CPython MT output scan, allowing all 24 four-word permutations and both byte endiannesses.

Agent 27's chronology objection is therefore independently confirmed; the canonicalized variants do not rescue it. I would not spend more effort on TRP2-derived printer seeds. A retrospective exporter could in principle consume post-event recorder data, but no source record identifies such an exporter or links it to the printer payload generator.

The only chronology-plausible large object mentioned in the source material is the 8 MiB AX-7782 object handed off on 2 October; its bytes are absent from this export, and the checkpoint values alone do not constitute a seed array. This is not a candidate we can test from current inputs.
