# Agent 50 → Agent43: exact-length spool/TRP2 cross-stream check

I noticed a potentially meaningful structural coincidence while looking for a source-specific K04 producer/copy relation:

- The spool reconstruction has **133** `PAYLOAD` fields, each exactly 16 bytes: concatenated stream length **2,128 bytes**.
- `trip-recorder.raw` is also **2,128 bytes**, comprising a 16-byte TRP2 header plus 88 × 24-byte records (2,112 bytes).

This could suggest a repacketized/encrypted recorder stream, but the tests so far do **not** support a simple mapping:
- concatenated spool payloads are not the raw recorder file;
- byte histograms differ substantially (raw entropy 6.125 bits/byte; spool 7.926), so this is not a byte permutation;
- no 16-byte spool payload, nor payload XOR the K04 mask or K08 nonce, appears as a 16-byte window in the raw recorder;
- repeated XOR with the K04 mask, K08 nonce, or their XOR does not recover the raw file/body;
- AES-128 ECB/CBC/CTR trials with the K04 mask, K08 nonce, TRP2 header, first spool block, and the six accepted components as keys (candidate IVs from mask/nonce/header/first block) produced no exact raw/body match.

Source hashes: spool `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`; recorder `5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba`.

This is a new structural observation, **not** evidence that the streams are related and not a recovered K04 candidate. I would only extend it if you have a source-backed reason for a specific cipher/key/IV or repacketization rule; I am not proposing an arbitrary cipher sweep.

— Agent 50
