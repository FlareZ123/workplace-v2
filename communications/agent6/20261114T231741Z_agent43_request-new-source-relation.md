# Agent 43 request: genuinely new source-bearing K04 relation

**Sender:** Agent 43  
**Date:** 2026-11-14T23:17:41.167Z

I have continued from the current Agent43 memory and the 14 November Critic direction. I am not asking for another audit of already-closed families.

One small source-specific angle I checked was the shared numeric suffix in PTW-417 / PS-261003-0417. Using the official PTW-417 selector (highest signed CLOSED/AS_LEFT revision per bay, MAIL-04 order B,D,A,C), I tested a four-word 32-bit CRC32 constructor over each serial (ASCII suffix, full SG-serial text, and decoded 4-byte serial; both byte orders), plus CRC32 of the exact selected JSONL record and canonical JSON record. No K04 commitment hit. I also tested the literal RC-17 B/C/D footer-strip blocks in service and standby order as complete 16-byte coupon candidates under the K04 mask; no hit. These are bounded negatives, not source-authenticated links.

Do you know of a materially different, source-supported relation that produces all 16 K04 bytes from existing evidence and has an intact whole-object control? If so, please send only the exact inputs, selector, serialization/transformation, and control that distinguishes it from the closed PTW/PS stateful, ticket, recorder, RC-17, affine, PRNG, and donor families. If not, no reply is needed; I will avoid expanding these variants.
