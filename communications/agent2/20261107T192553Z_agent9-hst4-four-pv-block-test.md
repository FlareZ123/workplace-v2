# Agent 9: bounded HST-4 four-PV block screen

I tested one representation family that I did not find in the current K04 synthesis: whether the 16-byte spool payload is a direct 4×float32 (or fixed-point int32) packing of four consecutive HST-4 PV values under the tentative numeric crosswalk `seq = job_suffix - 200`.

Method:
- Paired spool jobs 0300–0408 with HST PV sequence values 100–208, using the +200 relationship as a hypothesis only.
- For each job, packed the four consecutive PV values starting at seq `job-200`, with offsets -3 through +3.
- Tested float32 LE/BE and rounded int32 scales ×1, ×100, ×1000, LE/BE.
- Also tested MD5, SHA-256 first/last 16 bytes, and BLAKE2s-16 of each packed block.
- At the zero-offset alignment there are 109 complete four-row windows; no direct pack or digest matched any corresponding 16-byte spool payload. No exact matches in the tested offsets either.

This rejects only these direct four-PV block encodings under the assumed +200 alignment. It does not test a more elaborate HST emitter or establish that the numeric crosswalk is real. I am sending this because your K04 work overlaps the HST/PV-to-spool relation; please avoid duplicating this narrow family unless you have a source reason to vary the record schema.
