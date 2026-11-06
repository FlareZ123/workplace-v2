# Agent 5: NIST AES-128 CTR_DRBG stateful printer retry issuer, original K04 negative

**6 November 2026.** This is a new source-conditioned **complete physical-coupon** hypothesis following the prior HMAC_DRBG attempt. The unchanged original K04 slot commitment rejected **1,344 complete assignments, 1,176 distinct sixteen-byte coupons**. Independently retained 0417 same-job REQUESTED1/REQUESTED3 copied buffers and 0420 RECOVER ACK2 copied buffer also rejected every complete issuer prediction. A full planted synthetic accepted coupon was found exactly once.

## Concrete speculative mechanism

NIST SP 800-90A Rev.1 §10.2.1 describes a 128-bit AES CTR_DRBG with 128-bit Key and counter V, including a 32-byte no-derivation-function entropy seed, AES(V+1) output, and state update after each generation. It is historically documented as an available standard, **not** identified anywhere in this archive as actual printer firmware. This mechanism is distinct from earlier stateless AES header producers and this incarnation's HMAC_DRBG.

For original job PS-261003-0417 use either the 16:45 LABEL ACK1 payload as initialization entropy with the later 18:01 REQUESTED1, unknown 18:02 RECOVER ACK2 and 18:03 REQUESTED3 as successive outputs, or use the 18:01 REQUESTED1 payload as seed with just unknown 18:02 ACK2 and 18:03 REQUESTED3 as outputs. The disputed copied 18:02 payload is not used to seed or calibrate. Apply identical seed/configuration to original PS-261003-0420 STORES ACK1 and predict its independent 18:25 RECOVER ACK2 copy in full.

The finite source-defined input menu comprises 6 seed assembly modes, 8 second-half entropy inputs (nonce, mask, event hashes, zero and other source payload), 7 event-dependent additional inputs (including absent and zero, plus SHA256 of original job metadata), 2 optional output byte orders, and 2 0417 event histories. The full Cartesian product has **6 × 8 × 7 × 2 × 2 = 1,344** candidate assignments.

Original intact printer spool SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`, actual K04 route mask `8556C8CB6140A7F9A5123AC7571BEE1C`, and exact original full SHA256 K04 target `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0` are fixed and asserted in the read-only SFT.

## Actual original-source outcomes

Local original ZIP SFT returned:

```json
{"checks":1344,"original":0,"planted":1,"req1":0,"req3":0,"unique_coupons":1176,"watch":0}
```

Every complete coupon candidate was XORed with the original mask and its complete 256-bit SHA256 compared to the unmodified commitment. The planted complete physical coupon used the same AES stateful code, original routing mask and original full SHA256 acceptance path, with a separately constructed target and exact one-hit positive. The source controls are **copied spool values**, not separately authenticated physical media.

**Portable SFT:** [agents/agent5/k04_ctr_drbg_stateful_retry_sft.py](../agents/agent5/k04_ctr_drbg_stateful_retry_sft.py); local originally executed source `/mnt/data/h17_ctr_drbg_a5.py`. Depend on Python package `cryptography`; official NIST specification: https://csrc.nist.gov/pubs/sp/800/90/a/r1/final . The portable and locally run implementations use the same source inputs, model, candidate count and heldout constraints; independent CI execution of the portable file has not been claimed.

## Scope

This rejects exactly the 1,176 fully specified physical coupons produced by this finite proposed AES CTR_DRBG issuer family. The zero copied-source predictions also argue against it as a model of those specific copied rows. The authentic selected printed payload remains unavailable, and no coupon bit has become authenticated. Another AES initialization mechanism, external key, rekeyed print stage or non-DRBG producer is not excluded. K01/K02/K03/K05/K06/K07 still PASS, K04 and K08 unresolved and combined REC8/1 incomplete.
