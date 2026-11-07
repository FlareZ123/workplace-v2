# K04 original printer: exhaustive 32-bit XXH3-128 long-metadata publisher

**Agent31, 7 November 2026.** Original intact source, **17,179,869,184 full 128-bit predictions, zero historical whole-packet matches**. Four independent planted complete-output controls recovered exactly. K04 and K08 remain missing, six original slots pass.

## New candidate-producing model

A printer could issue a deterministic 128-bit value by hashing the complete job header with a short firmware/legacy seed. This hypothesis is exploratory: no original hardware record claims an XXH3 emitter. The standardized XXH3-128 seeded hash has a 64-bit seed parameter, and firmware commonly uses narrower integer seeds. This study exhausts the full 32-bit seed subspace **for input lengths 32,61,87**, different algorithm branches from the [earlier exact 64-bit short-message inverse](h17-k04-xxh3-128-short-message-inverse-20261107.md). No selected disputed ACK2 bytes are used.

Original source: resources/evidence/print/spool-reconstruction.log, SHA256 7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083, directly verified from all source bytes in the reproducer. Its first intact packet is PS-261003-0300, 07:00 UTC, attempt1 ACK/LABEL/store, full payload FBBBC54356483F5864BB3F06794518A5. The source-only gate requires an exact full 16byte match under one of four low/high 64bit word order and byte-endian serializations.

Four messages, chosen from authentic first-row metadata before exhaustive testing:

| Form | Input message | Bytes | Seeds | 32bit-prefix coincidences | Whole packet |
|---|---|---:|---:|---:|---:|
| A | 2026-10-03T07:00:00+00:00 JOB=PS-261003-0300 ATTEMPT=1 STATE=ACK CLASS=LABEL DEST=store | 87 | 4,294,967,296 | 2 | 0 |
| B | JOB=PS-261003-0300 ATTEMPT=1 STATE=ACK CLASS=LABEL DEST=store | 61 | 4,294,967,296 | 3 | 0 |
| C | PS-261003-0300 pipe 1 pipe ACK pipe LABEL pipe store | 32 | 4,294,967,296 | 4 | 0 |
| D | PS-261003-0300/1/ACK/LABEL/store | 32 | 4,294,967,296 | 3 | 0 |
| **Total** | | | **17,179,869,184** | **12** | **0** |

Form C literally uses the ASCII vertical-bar delimiter between the five fields. The 32-bit-prefix coincidences match only one short projection and are not full-packet hits. Every possible 32-bit seed in each form was tested with no gaps. The four output serializers cover both 64-bit word orders and both per-word byte-endian orders.

### Planted controls, provenance and reproducer

Each complete original-source scan was executed with original file SHA256 assertion, intact first-row recognition, and a separate **genuine seeded XXH3-128 full-output positive at seed 0xABCDEF01**. All four source tests yielded **zero** source whole-packet hits and **one** exactly recovered planted whole-output positive; adjacent seed 0xABCDEF00 produces a different full output. A second reference fixture at seed 0x12345678 is printed for each message and all four complete original outcomes were repeated after the source-pin assertion was added.

Portable [C++17 source-pinned XXH3 longlabel SFT](../agents/agent31/k04_xxh3_longlabel_uint32_sft.cpp) uses OpenSSL SHA256 for the original byte pin, official xxHash v0.8.x header-only API and OpenMP for independent seed ranges. It accepts the fixed input-form index 0..3, a half-open seed interval in 0..2^32, and CPU thread count. Four complete runs (one per form) reproduce all table values. Original materials, candidate file, K04/K08 commitments and official verifier are unmodified.

## Historical limit and research decision

No common issuer seed in this exact XXH3/32bit-seed/long-header family can produce the **first intact source packet**, so no selected coupon is justified under that producer and the exceptional late RECOVER records need not be fitted. This is a whole-source historical negative for a distinct standardized 128-bit hash. It does not eliminate full 64-bit XXH3 seeds on long messages, other original metadata formats, a different producer, or a separate physical-copy mechanism. The hypothesis had no independent source attestation, so indiscriminate new header variants have weak evidential value. The original selected physical K04 coupon still has zero authenticated bits and K08 final author-selected text remains unquoted; combined REC8/1 is INCOMPLETE.
