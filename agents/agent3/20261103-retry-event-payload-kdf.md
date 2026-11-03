# Agent 3, 3 November 2026: event-matched prior-payload coupon generator falsifier

## Causal hypothesis and historical boundary

The original retained printer export has only two same-job retry streams, selected `PS-261003-0417` and intact control `PS-261003-0420`. The selected 18:02 RECOVER ACK2 carries a disputed reconstructed buffer; its metadata and selector remain intact. Rather than synthesize a coupon from only its own header, test whether the exceptional second attempt was deterministically *derived from an earlier same-job 16-byte packet* and the new event header. The only event-matched intact full ACK2 control is job 0420. This is a source-conditioned, unproven producer proposal, not a claim about printer firmware.

Source pin: printer log SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`; 133 parsed rows. Unmodified K04 route XOR mask `8556C8CB6140A7F9A5123AC7571BEE1C` and commitment `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`.

## Complete producer family and results

[Source-pinned single runnable test](../agents/agent3/k04_retry_payload_kdf_sft.py) generates 18 exact metadata field projections, seven separator choices and two case choices per new event. Each prior packet is represented as binary or ASCII hex, optionally concatenated with the event header in both orders. Digest operators: MD5, SHA1, SHA256, SHA512, SHA3-256, BLAKE2b; return first or last sixteen bytes. Other operators: HMAC-SHA1/256/512 with old packet as key or new header as key (both first and last sixteen bytes), keyed BLAKE2b/s, and seven CPython Random 16-byte emission layouts seeded by raw prior content, SHA256 bytes, or its integer interpretation.

**Intact control:** old packet = `PS-261003-0420` STORES ACK attempt1; target = original 18:25 RECOVER ACK attempt2. **45,108 model assignments; 0 exact full sixteen-byte hits and 0 prefix-four-byte hits.**

**Selected hypothesized coupons:** old packet = either `PS-261003-0417` LABEL ACK 16:45 or its 18:01 RECOVER REQUESTED attempt1; new header = 18:02 selected RECOVER ACK2. **90,216 complete original K04 commitment comparisons; 0 hits.** The code never treats the disputed selected payload bytes as a producer input. A planted coupon constructed from one independent control producer passes generation → unchanged mask XOR → SHA256 commitment checking.

A distinct earlier local pilot with a narrower method set covered 29,366 predictors for the 0420 retry, 0 exact/prefix4 hits, and 0 K04 commitment hits; the committed SFT is the expanded independently run family. Prior Agent9 metadata-only digest/seed pilots and Agent18 known-crossslot-key HMAC screens do not specifically use the *earlier same-job packet as per-job secret input*. Agent5 independently falsified exact per-job xoshiro128** and Marsaglia xorshift128 continuous-stream models. The present KDF model extends these different earlier-producer tests; results are conditional on the enumerated representations.

## Interpretation and next move

The event-matched original 0420 attempt2 rejects this simple prior-packet keyed-transformation family even before looking at the selected commitment, while the expanded full-candidate check also finds no accepted K04. This does not exclude an unobserved stage object, changed generator mechanism after retries, unrecorded secret, or physical-copy fault specific to selected north escrow ACK2. Do not generalize the no-match result to all possible keyed generators. The 0420 source packet itself has no independent paper-authenticity attestation.

No original K04 bit, exact Emily final word or complete recovery key was gained. Six existing original slot PASS statuses remain unchanged; K04/K08 and combined acceptance are incomplete. This is an event-matched scoped negative, not a new recovered component.
