# Direct HMAC16-as-ESC-N coupon hypothesis — bounded negative

**Date:** 2026-11-15  
**Agent:** 17  
**Scope:** One explicit K04/K08 joint-carrier construction; not a general claim that the slots are independent.

## Question

Could the 16-byte K04 ESC-N coupon be exactly the 16-byte K08 component generated from a candidate desk phrase?

The proposed relation is:

```
hmac16 = HMAC-SHA256(K08.desk_nonce, normalized_phrase)[:16]
K04_component = hmac16 XOR K04.masked_component
```

MAIL-16 explicitly excludes ESC-S as an input to the keeper's phrase, but does not say ESC-N is a K08 input. The routing record carries both the K04 mask and K08 nonce, which makes a direct same-block interpretation tempting but does not establish a relationship. Importantly, the K04 route rule itself says the RECOVER payload bytes are opaque, not a digest or text. Therefore `coupon = HMAC16` is source-inconsistent; this enumeration is retained as a bounded boundary check, not as a source-supported K04 constructor.

## Frozen candidate family

Reused the exact phrase grammar already defined in [Agent 9's caption-seeded printer test](../agent9/k08_hmac32_printer_coupling_sft.py), without adding, removing, or editing any phrase:

- 32 sea/outside clauses
- 25 night/watch clauses
- 50 people/table clauses
- 8 temporal opening prefixes
- all 6 orders of the three semantic strands
- 6 connectors at each of the two joins

Total: **69,120,000 distinct candidate phrases**.

For each candidate, the test computed the K08 HMAC16, XORed it with the exact K04 route mask, and compared SHA-256 of that 16-byte result with the unchanged K04 acceptance commitment.

## Pinned inputs

- Crew-note source: `resources/evidence/crew/noticeboard-and-desk-notes.txt`  
  SHA-256: `13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb`
- Routing source: `resources/evidence/recovery-routing.json`  
  SHA-256: `f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5`
- Acceptance source: `resources/acceptance.json`  
  SHA-256: `681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f`

The source motivation is pinned to `resources/evidence/mail/16.eml` (SHA-256 `02535cc5966a9215d01ecada4a14b6a403d78ca8d09310a5c3cf1a574f817a08`). The frozen phrase-family definition is pinned to Agent 9's script Git blob SHA-1 `01680d0aaa88bb0bb36db319f9598f704dcb5caa`. The reference runner asserts all four source SHA-256 values and that Git blob before execution. The executable reads the nonce, mask and target directly from the pinned files. No candidate, acceptance, routing, source, or verifier file was modified.

## Execution and result

The full 69,120,000-candidate family was evaluated using an optimized C++/OpenSSL implementation with incremental HMAC context copies and SHA-256. The synthetic positive control passed.

| Check | Candidates | Commitment hits |
|---|---:|---:|
| K04: `SHA256(HMAC16 XOR mask)` | 69,120,000 | **0** |
| K08: `SHA256(HMAC16)` | 69,120,000 | **0** |

The K08 result is the existing independent run of the same frozen family documented in [Agent 9's result](h17-k04-k08-full-hmac-caption-seeded-printer-source-test-20261107.md). This Agent 17 run adds the K04 commitment check for the direct coupon identity.

A slower reference implementation is preserved at [`agents/agent17/k04_k08_direct_hmac16_coupon_sft.py`](../agents/agent17/k04_k08_direct_hmac16_coupon_sft.py). It imports the frozen phrase family unchanged and supports chunked execution by opening-prefix index.

## Conclusion and boundary

**The direct identity `ESC-N coupon = K08 HMAC16` has zero K04 hits in this 69.12-million-phrase family and is already inconsistent with the K04 route's explicit opaque-payload rule.** Treat this as a bounded rejection of a tempting direct-digest interpretation, not as evidence that K04 accepts a digest-based constructor.

The opposite direct identity, `K04_component = K08_HMAC16`, is algebraically impossible: the committed SHA-256 values differ (`K04 = 930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`; `K08 = 285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747`). The tested coupon identity and this opposite component identity therefore close both simplest same-block interpretations. This does not rule out a native ESC-N print object containing a rendered copy of Emily's wording, nor a different source-defined relationship between the two slots. It does not recover any K04 coupon bytes or K08 final words. The native PS-0417 spool/media and Emily's literal final envelope margin remain the target-bearing evidence.

The K04/K08 joint-carrier hypothesis should now be described as *media-level only and unconfirmed*; do not repeat this exact HMAC16-as-coupon search unless the phrase family or source evidence materially changes.
