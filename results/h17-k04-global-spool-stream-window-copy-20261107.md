# K04: global spool byte/nibble stream-window copy test

**Agent 13 | 7 November 2026 | 6,290 complete original K04 comparisons; zero matches.** The selected physical coupon remains unauthenticated; the six accepted slots and original verifier are unchanged.

## Hypothesis

A retained-fragment or copy-stage boundary error might have taken the selected 16-byte coupon from a **global spool payload stream** rather than from one complete row. This differs from the already tested three-retry-local byte/nibble mixers and exact whole-packet replay: the candidate can begin at any byte or hexadecimal nibble offset and can cross any intact row boundary.

The source-pinned test first excludes the disputed selected row129 entirely. It concatenates the 132 remaining 16-byte payloads in original chronological order, then checks every contiguous 16-byte window in:
1. the raw byte stream; and
2. the concatenated uppercase hexadecimal stream, with every character offset tested, including odd-nibble starts.

For each complete candidate coupon P, the unchanged K04 reducer is `P XOR 8556C8CB6140A7F9A5123AC7571BEE1C`; SHA256 of all 16 resulting bytes is compared to the unchanged full K04 commitment `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`.

## Original-source execution

The standalone [source-pinned SFT](../agents/agent13/k04_global_spool_stream_window_sft.py) asserts the original spool, route and acceptance SHA256 values before parsing. It verifies 133 spool records, excludes row129 by its exact job/attempt/state/class marker before extracting payloads, and uses only the 132 intact payloads.

| Candidate stream | Complete 16-byte windows | Original K04 hits |
|---|---:|---:|
| Chronological raw payload-byte concatenation | 2,097 | **0** |
| Chronological payload-hex concatenation, every nibble offset | 4,193 | **0** |
| **Total** | **6,290** | **0** |

Two independent planted full-target controls were recovered exactly at byte offset123 and hexadecimal-nibble offset321. The source run reports all three source pins PASS and both controls PASS.

## Interpretation and boundary

The original K04 coupon is not any contiguous 16-byte window in either of these two global stream representations. This rejects only the specified chronological concatenation and arbitrary-offset window model. It does not address noncontiguous selection, transformed rows, metadata-inclusive buffers, a hidden staging object, or a physical coupon absent from the retained export. The spool ACK still attests dispatch rather than media integrity, so this negative does not authenticate any K04 bit.

No original resource, routing, acceptance, candidate, or verifier was modified.
