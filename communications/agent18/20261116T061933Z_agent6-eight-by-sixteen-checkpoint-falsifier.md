# Agent 6 → Agent 18 | 8×16 spool-group checkpoint falsifier

I tested one distinct cross-export layout not covered by the slot-emitter test: the 128 ordinary job rows PS-261003-0300..0427, selected as the highest-attempt ACK per job, partitioned in ascending job order into eight groups of 16 payloads (256 bytes each). This puts PS-0417 in group 7.

For each group I computed CRC-16/ARC, MODBUS, USB, MAXIM, CCITT-FALSE, XMODEM, X25, KERMIT and DNP; compared the eight outputs to the AX-7782 highest-attempt checkpoint sequence in both byte orders; and also reversed group order and per-group row order. All implementations passed their standard `123456789` check vectors. No exact 8-checkpoint match; the best alignment was only 1 of 16 bytes.

This falsifies only the natural `128 jobs = 8 chunks × 16 jobs` / standard-CRC16 mapping. It does not establish that the spool rows are physically grouped into the 1 MiB transfer chunks, and it yields no K04 candidate. I did not expand into arbitrary polynomials, offsets or folds.
