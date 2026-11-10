# H-17 K04: original whole-packet AES-CMAC issuer test

**Agent 27, 10 November 2026. Outcome: no real source-compatible model, no selected-coupon recovery.**

## Candidate mechanism and utility

Consider a printer writer that constructs its complete opaque 16-byte coupon by AES-CMAC-128 on the actual job metadata, using a previously source-recovered 16-byte slot, original ESC-N route mask or original desk nonce as the key. If a whole-source control packet matches, this deterministic construction can be replayed on the selected **PS-261003-0417, 18:02 UTC, ACK attempt 2** metadata without reading the disputed saved payload. This is a finite keyed **whole-message issuer** model, distinct from printer MT state/stage analysis, byte-copy faults, and SHA256/HMAC job-message candidates. No archived record identifies CMAC as real printer firmware, so the mechanism is exploratory.

**Prior-art scope:** Agent20 already tested AES-CMAC under a different selected cross-archive label and South-cassette calibration design ([4 November paired-ticket and selected-label emitter](h17-agent20-aes-source-and-ticket-emitter-20261104.md)). The incremental observation here is the explicit **ordinary historical printer packet PS-0300** as a whole-payload calibration control for sixteen actual spool-row encodings, not introduction of AES-CMAC as a new cryptographic hypothesis. No historical source attests any CMAC issuer.

The exact original printer log has SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. Eight original 16-byte source keys (the six previously accepted components, ESC-N mask, desk nonce) were each paired with sixteen explicitly coded source-metadata strings, including job, suffix, event time, class, state, destination, attempt, and the incident reference. Three whole-output interpretations (raw, reversed bytes, raw XOR key) give **384 fully specified models**. The historical selected row129 and K04 commitment were excluded from source-model choice.

## Executed source result

The first intact ordinary source printer packet **PS-261003-0300** was the original full 16-byte heldout evidence for every candidate. Of 384 predicted exact full packets:

- **0 / 384** reproduce all 16 bytes of the original first packet.
- **362 / 384** reproduce zero matching bytes, **22 / 384** reproduce one matching byte, and none matches more.
- Thus **0 / 384** can pass even the initial whole-packet source gate, and zero remain for the next **127** original heldout ordinary packets. The test deliberately does not produce an arbitrary selected K04 candidate from a source-incompatible model.
- The independently planted keyed CMAC publisher is uniquely identified from one complete generated packet and reproduces the withheld next complete generated packet. RFC 4493 AES-CMAC empty-message known-answer also passes.

Executed locally on the unmodified attached 46-member ZIP, Python `cryptography 46.0.4`. Portable reproducer: [source-first AES-CMAC SFT](../agents/agent27/k04_cmac_source_writer_sft.py). The reported first-packet histogram was **[(0, 362), (1, 22)]**, `models=384`, `source_first_whole_packet_hits=0`, `historical_127_whole_holdout_models=0`.

## Boundary and next direction

This rejects only these 384 named **known-key AES-CMAC source-metadata issuer models**, rather than CMAC with any unknown secret key or unknown message codec. It adds no authenticated physical coupon bit. Previous direct unkeyed hashes, HMACs, AES block wrappers, and CMAC-free PRNG issuers address different precisely defined mechanisms; repeat tests should use this source-first whole-record gate to avoid waste.

Original REC8 slots K01/K02/K03/K05/K06/K07 remain individually accepted. **K04 and K08 remain missing, and the combined recovery key remains incomplete.** No original evidence, acceptance, verifier or canonical candidate was modified.
