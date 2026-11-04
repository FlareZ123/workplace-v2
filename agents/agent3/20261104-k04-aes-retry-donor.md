# K04: AES-128 previous-ACK coupon producer with independent same-job holdout (4 November 2026)

**Outcome: 0 of 1,520 original complete K04 commitment matches; 0 of 1,520 exact intact 18:25 ACK2 holdout matches.** This is a *new conditional complete-coupon family* (AES block transformations keyed by the earlier ACK payload) and is not evidence that the physical coupon is AES-generated. Six original slots still PASS, K04/K08 missing.

## Source-defined target and analogue

Immutable source `resources/evidence/print/spool-reconstruction.log`, SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. The original route selects `PS-261003-0417` RECOVER ACK attempt2 at 18:02Z; its earlier same-job LABEL ACK1 occurred at 16:45, and the route mask is `8556C8CB6140A7F9A5123AC7571BEE1C`. The copied ACK2 payload remains disputed and is **never used as generator input**.

The strongest locally available *same-job, same-class-transition target analogue* is `PS-261003-0420`: 17:00Z STORES ACK1, followed by independently retained 18:25Z RECOVER ACK2. It provides a genuine **complete 16-byte heldout output** for a possible previous-job-packet→later-recovery-coupon producer. The earlier ACK1 is a candidate key, and exact packet identity/attempt fields are arguments. Different class of first ACK (STORES versus LABEL) is an important comparability limitation.

## Frozen finite mechanism

For each same-job pair, derive five AES-128 keys from the **earlier** ACK1 full 16 bytes: identity; SHA256 first16; MD5; XOR with route mask; XOR with K08 desk nonce. Encode the later job using 19 complete 16-byte plaintext encodings: ASCII job ID (space/null padded), 16-byte integer job and timestamp in both byte orders, seconds-in-day in both orders, packed job/timestamp/attempt integers in both byte orders, earlier raw payload, and four metadata-string schemas each reduced using MD5, SHA256 first16, or null padding where length permits.

Before AES encryption XOR with one of four 16-byte tweaks (zero, older ACK1, mask, nonce); after the encryption XOR with an independently chosen tweak from the same four. This gives `5 × 19 × 4 × 4 = 1,520` explicitly named AES-128 full-packet producers. For each, first compare the *complete* predicted 0420 ACK2 packet with the untouched 18:25 source. Separately derive the predicted 0417 physical coupon from its earlier LABEL ACK1, XOR the original K04 route mask, and compare SHA256 of the resulting 16 bytes against the original K04 commitment `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`.

## Executed read-only result and controls

Local Python 3.13 + `cryptography 46.0.4` against exact original ZIP bytes; full source parser yielded 133 records. `1,520` models, **zero** full control matches, **zero** two-byte prefix matches, **zero** original K04 acceptance matches. Standard NIST AES128 test vector `00112233445566778899AABBCCDDEEFF` with key `000102030405060708090A0B0C0D0E0F` produced `69C4E0D86A7B0430D8CDB78070B4C55A`. A planted complete 0417 AES-derived coupon, passed through the authentic route XOR and original SHA256-style outer reduction against an isolated synthetic target, was recovered **uniquely** from all 1,520 candidate models.

The executed local one-file SFT is `/mnt/data/h17-research-agent3/agents/agent3/k04_aes_retry_packet_sft.py`, SHA256 `c37c168eac900970f507e60f8ea99a0843a6058ac9ca5d71c6fc991b23b3028f`. This location is session-local unless its bytes are separately preserved. It imports `cryptography.hazmat.primitives.ciphers`, reads only repository `resources/`, asserts source SHA, uses the two real same-job ACK pairs, and emits exact model and hit counts.

## Inference and next mechanism

All named previous-ACK AES transformations fail the independent full-packet analogue and the selected complete commitment. Earlier Agent3's HMAC/BLAKE2 keyed previous-packet model was a distinct cryptographic reducer; this AES result does **not** reproduce its digests or rule out all PRNG/cryptographic encoders. There is no original evidence that a printer uses AES, or that even the intact 18:25 copied payload equals its physical coupon. Do not enlarge arbitrary AES key/tweak dictionaries without a source-identified key schedule. The open target-facing direction remains a production/copy-stage relation supported by actual same-lineage event controls, or direct recovered 18:02 media bytes.
