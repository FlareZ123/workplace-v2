# K04: cancel a shared printer-secret pad between south and north cassette tickets

**Agent 41 | 4 November 2026 | 2,209,194 complete original K04 checks, zero acceptance matches.** Six previously accepted components remain unchanged, K04 and K08 unresolved, combined REC8/1 INCOMPLETE.

## Distinct source-to-full-K04 mechanism

The original print-fleet return register directly relates the selected north ESC-N job0417 with cassette L-29/N tickets ST-094, ST-081, ST-106, ST-099, ST-112, and an intact-copied south ESC-S job0448 with cassette L-29/S tickets ST-130, ST-151, ST-121, ST-135, ST-142. The 18:24 source-visible south RECOVER ACK1 coupon is **234BE186E97EE05830909790E336109E**. The disputed 18:02 north selected ACK2 copied payload is **never fitted or consulted** in this experiment.

A new hypothetical cassette emitter could use an unknown **common 16-byte printer pad U**, then XOR a cassette-specific deterministic ticket mask F(ticket list, route metadata):

    coupon_S = U XOR F(S)
    coupon_N = U XOR F(N)

With this architecture the *unknown U cancels exactly*. Thus the original visible south full coupon produces a **complete** hypothesized north physical coupon:

    coupon_N = copied_coupon_S XOR F(S) XOR F(N)
    K04_candidate = coupon_N XOR original_route_mask

A known pad is unnecessary; a complete north ticket-derived candidate can be tested directly against the immutable full K04 SHA256 commitment. Crucially this differs from Agent10's and Agent20's previous per-cassette digest/AES/PRNG tests, which attempted to reproduce the south coupon directly as F(S) and found zero. The earlier negatives do **not** exclude a cancellable shared U.

The same-day two-lane/part-position linkage makes the model explicit and testable, but the original register does **not** say that the historical printer used ticket whitening or a common pad. The original south ACK is independently retained in the spool yet its paper-media fidelity is also unverified. Therefore a zero target check has precisely conditional meaning.

## Frozen generator family and complete original experiment

Borrow the **2,106 original paired ticket+metadata serializations** of Agent10's source-coupled holdout so that no new unlinked filename or label lottery is introduced. Each includes five three-digit/decimal/ST-prefixed ticket codes separated by seven fixed delimiters or five binary integer layouts, optionally bracketed by one same-role field such as route/job/attempt/timestamp/account/filer reference/destination with five documented separators. Both lanes use the identical encoding.

For each paired input produce one fixed 16-byte mask by:

- 25 digest/HMAC16 choices: MD5, SHA1, SHA256, SHA512, SHA3-256, BLAKE2s, BLAKE2b each at first/middle/last16 positions, plus first16 of HMAC-SHA256/HMAC-SHA512 keyed by original desk nonce or authentic K01;
- four standard CPython Random seed types (raw bytes, Latin-1 text, big/little integer) at each of the first **256** coupon output phases.

Every complete north candidate is XOR-reduced with the **unchanged original** route mask 8556C8CB6140A7F9A5123AC7571BEE1C and SHA256-tested against K04 slot 930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0.

| Source-paired family | Complete model assignments | Original full K04 matches |
| --- | ---: | ---: |
| 25 digest/HMAC roles | **52,650** | **0** |
| 4 seed views times 256 PRNG positions | **2,156,544** | **0** |
| **Total** | **2,209,194** | **0** |

Assignment count is exact, not a guarantee of that many unique candidate byte strings. Two complete seeded positives verify the algebra: independently plant a shared 128-bit U, generate the south coupon using one fixed digest mask and then one genuine CPython stream phase 73; both recover the *entire* correct paired north coupon, each once in its designated control. The authentic K04 result is zero.

## Independent source pins and reproducibility

[Portable read-only single-file SFT](../agents/agent41/k04_cassette_common_pad_sft.py) executes directly against the same original repository resources (or the original ZIP extracted as root). SHA256 source pins:

- fleet return register 10c3a6e46b2c8475fd5fd8333cd8546633bda7ca3eac4e813ac059cd045e3cbf;
- spool 7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083;
- route f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5;
- acceptance 681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f.

The exact implementation was executed successfully against the uploaded 46-member, SHA256-pinned ZIP extraction. Its output was:

    PAIRED_SOURCE_FORMS 2106
    COMPLETE_K04_COMPARISONS 2209194 {'digest': 52650, 'python': 2156544}
    SYNTHETIC_FULL_COUPON_POSITIVES {'digest': 1, 'python': 1}
    ORIGINAL_K04_HITS 0 []

This result excludes exactly those F transformations if the north and south print coupons indeed share a common XOR pad U and the original south buffer is reliable. It does **not** exclude route-specific unknown pads, nonlinear secret-sharing, other encodings, cassette-independent physical generation, or damaged south copied media. No original target byte, supplier ticket or K08 caption word was inferred; the source PDF and public corporate site offer no extra authenticated coupon here. Do **not** repeat this exact common-pad family with a renamed hash function. The productive next distinction is whether an original independent same-key sibling with a **complete, authenticated physical coupon** or recorded ticket-to-coupon relation exists.

**Status:** K01/K02/K03/K05/K06/K07 PASS; K04 and K08 MISSING; combined INCOMPLETE; accepted=false.
