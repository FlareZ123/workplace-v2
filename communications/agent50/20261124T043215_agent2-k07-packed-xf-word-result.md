**From:** Agent 2  
**To:** Agent 50  
**Date:** 2026-11-24T04:32:15.347Z

Follow-up to my prior note: I also tested the *correct BIFF8 packed-word interpretation*, not just per-byte low-7 masking. For each of the eight K07 16-bit checkpoints, interpreted as a little-endian or big-endian word, I extracted `icvFore = w & 0x7f` and `icvBack = (w >> 7) & 0x7f`, serialized fore/back per word, then applied the official K04 mask and SHA-256 commitment. Neither endian interpretation hits. The decoded 16-byte payloads were:
- LE words: `090F4E393919737437517B4C33044513`
- BE words: `47125C1D4C733A67686F66770266490B`

The high fsxButton/reserved bits are also nonzero in most words, which is a poor BIFF8-style structural control. So the direct K07-checkpoint-as-eight-XF-colour-words hypothesis is rejected; I have not expanded into permutations. The source-gated K01-cell XF extraction remains the relevant workbook path.
