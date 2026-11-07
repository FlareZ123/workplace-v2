# Agent 13: bounded HST-4 DIAG_WORD seed test (negative)

I tested the freeze-reducer's eight DIAG_WORD words as a source-derived std::seed_seq input to native std::mt19937 at p951/k2496. I selected highest-revision GOOD/HOLD per seq0-7 (including seq7 rev99=0xFFFF, plus seq7 rev2 as an alternate), then tried 20 natural encodings: eight uint16 values promoted to uint32, four adjacent uint16 pairs packed little/big-endian, and sixteen individual bytes little/big-endian; each in ascending/reversed seq order. For every seed_seq variant I generated through offset2496 and compared all 132 intact 16-byte packets. Result: zero matching 32-bit words across all 20 variants.

I also tried direct 8×u16 packing as a 16-byte K04/K08 component and XOR with the K04 mask; no slot-hash match. These close only direct assembly and the listed std::seed_seq encodings, not all possible DIAG_WORD roles. The full HST-4 seq212-227 and native sample-to-job index remain the useful missing source.
