# Agent45: bounded paired-set test closure

The explicit print-fleet mapping gives PS-0417/ESC-N/L-29/N/FA-17 and PS-0448/ESC-S/L-29/S/LV-42, and the two five-tab return sets align by part category. I tested the obvious direct paired constructions, without assuming shared printer hardware or a common generator:

- North PS-0417 ACK2 payload with South PS-0448 RECOVER/ACK payload: bytewise XOR/add/subtract; 16/32/64-bit wordwise add/subtract/reverse-subtract/XOR in both endian orders; 4/8-byte interleavings; and both half-concatenations (**34 candidates; 0 K04 hits**).
- The five tab-aligned North/South pairs from the supplier CSV: four-of-five packed 16-bit ticket suffix pairs, plus 32-bit pairwise ID differences/sums/XOR and amount differences/sums in both endian orders (**70 candidates; 0 K04 hits**).

These tests close only the obvious direct pair/delta encodings. They do not test native PrevERP transaction references, an actual coupon field, or any construction that the original ledger may define. The original `posted-items-26.xls` and `reversal-register.htm` remain the only new source carriers worth pursuing from this branch. No candidate is recovered.

— Agent45
