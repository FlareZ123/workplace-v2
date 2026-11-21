# H-17 K04: AES issuer keyed by a changing four-bay PTW state

**Agent 3 | 21 November 2026 | executed complete-coupon experiment, bounded negative.** No original K04 accepted; six established slots remain valid and K08 remains unresolved.

## Distinct model and fixed input

The intact original `maintenance/seal-receipts.jsonl` has singleton PTW-390..416 source serials and PTW-417's revisioned four-bay state. Each of PTW-395..416 has an independently surviving intact same-suffix PS-0395..0416 ACK payload, 22 complete source pairs. This permits a full historical holdout for a hypothetical relation even though the permit-number-to-printer-job join is *not company-attested*.

Prior [rolling PTW AES issuer](h17-k04-rolling-ptw-bay-state-issuer-20261109.md) treats the accumulated 16-byte PTW four-bay state as the AES **input block**, with a fixed known key and possibly an arbitrary pad. This new independent reversible source model instead treats that PTW state as the *changing AES-128 key*, with one shared unknown 128-bit plaintext/ciphertext:

```
  key[permit] = pack(latest signed CLOSED AS_LEFT serial per bay through permit)
  observed_printer_payload[permit] = AES128_{key[permit]}(fixed_unknown_block)
```

Both encrypt and decrypt orientations are tested. First complete source pair **PTW-395/PS-0395 alone** gives the entire 128-bit common block through AES inversion. All **21** PS-0396..0416 payloads are independent complete-object holdouts, withheld from this inversion. Predict the selected PS-0417 attempt-2 coupon entirely from the final PTW-417 state, without reading the disputed copied 18:02 ACK2. Then apply the *unchanged* source route mask and the *full* original K04 SHA256 commitment.

The source's final original B/D/A/C selected four-bay bytes are `D7DAD6BC9714519B7DAD0AD4BE8E87FD`. We test both B/D/A/C and A/B/C/D state bay orders, with whole-four-word reversal and independent byte reversal inside every four-byte word. For each, test printer payload serializers with the same two independent word/byte reversal booleans, and both cipher directions: **2 × 4 × 4 × 2 = 64 complete issuer models**. All models derive their common block from only the first intact source pair. This is a *different key role* from the earlier fixed-key AES and direct/PTW-as-input tests.

Source pins: original PTW SHA256 `c00944558636fbcc7e91b81e8e838ffd13fcd5a30d121b41951888766a8a0e32`, spool SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`, original ZIP SHA256 `e778552c555fac652e24fd09e1c4f31bd066b4686e624b91f6e94e1d64342bf7`.

## Executed original outcome

| Exact measurement | Observed |
| --- | ---: |
| Original source-calibrated AES models | 64 |
| Intact historical 16-byte printer holdouts per model | 21 |
| Models reproducing *all* 21 holdouts | **0** |
| Best number of exact whole holdouts for any model | **0** |
| Fully generated K04 original SHA256 commitment hits | **0** |
| Synthetic hidden-common-block reproductions, all 21 holdouts and final blinded coupon | **64/64 PASS** |

A source-equivalent original-ZIP run was executed locally using Python's `cryptography` AES cipher implementation. The independent synthetic positive uses a nontrivial constant hidden block, generates every modeled source packet from the same historically selected PTW states, reconstructs the block *only* from the planted first pair, and checks all 21 planted holdouts and the final complete predicted coupon. The result is a strong source incompatibility for this exact **changing-key/fixed-block** issuer, not evidence of a historical device using AES.

## Limitations and decision

The exporter explicitly warns that printer ACK payload integrity is unauthenticated. The matching numeric PTW/PS suffix may be incidental, and no issuer specification supports AES here. Therefore, failure against 21 preserved printer copies rules out only the tested issuer at the copied-file stage. It cannot exclude a print-media transformation after issuance, a per-job plaintext, other key schedules, variable state, a changed issuer, or absent original evidence.

**No physical selected K04 bit is recovered.** The 64 complete proposed coupons fail the unchanged K04 commitment; no K08 wording is recovered. The canonical candidate, evidence, routing, acceptance and verifier remain untouched.

Reproducer: [Agent3 AES changing-key SFT](../agents/agent3/k04_ptw_rolling_aes_key_sft.py). The new source inversion should not be expanded by varying arbitrary salts or invented keys; future work needs a stronger independent producer discriminator or a selected physical coupon/full-caption carrier.
