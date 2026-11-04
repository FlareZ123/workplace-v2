# H-17 K04: ChaCha20 source-derived event-coupon producer test

**Agent 47 | 4 November 2026 | Entire source-derived ChaCha20 candidate family rejected; no seventh recovered component.**

## Source-attested boundary and distinct idea

The selected 18:02 UTC `PS-261003-0417` attempt-2 RECOVER ACK fixes the K04 routing **selector**, but the copied 16-byte `A9A9DC5731A5E2AE879C47215C2559D5` does not validate against the K04 commitment after XOR with the original mask. We deliberately withhold this copied selected payload from model construction and use only unselected intact printer records to discriminate a different producer.

This test asks whether the printer was a **counter-based ChaCha20 keystream publisher**, capable of deterministically emitting a complete coupon from a recovered source-derived key and event counter/nonce. ChaCha20 is structurally distinct from the prior AES header issuer, GHASH affine publisher, PCG/xoshiro state inversion, Philox and MT-state analyses. Filename inventory of the original v1 and current v2 research showed no predecessor ChaCha SFT. **The historical source never identifies ChaCha20, a cipher key or a nonce policy**. This is exploratory model discrimination, not authentic printer identification.

## Frozen full-coupon construction

Use the original preserved printer log, SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`, 133 rows. Exclude the disputed selected row index 129 from producer fitting. Source key material consists of six accepted 16-byte components K01 K02 K03 K05 K06 K07, the recorded 16-byte K04 mask and the K08 16-byte desk nonce, in that fixed order. Construct 72 ChaCha 256-bit keys: the SHA256 of each of those eight 16-byte inputs, plus **all 64 ordered concatenations of two inputs**, including self-pairs.

For every original row and selected row, test six event nonce formulas:

1. Twelve zero bytes.
2. First twelve bytes of the original route mask.
3. First twelve bytes of the original desk nonce.
4. First twelve bytes of `SHA256(ASCII(job ID))`.
5. First twelve bytes of `SHA256(ASCII(job|attempt|class|destination))`.
6. Eight-byte little-endian Unix event seconds, followed by four-byte little-endian attempt.

Test five 32-bit little-endian counters: zero, one, original 0-based row index, numeric job suffix, or event seconds modulo 2^32. The 32-bit counter and 96-bit nonce are passed to `cryptography.hazmat.primitives.ciphers.algorithms.ChaCha20`, which implements the current IETF-style 4/12 layout. Generate a complete 64-byte keystream block. Test 12 complete 16-byte serialization layouts: any of the four consecutive quarters, in native order, reversed order of four-byte words, or byte-reversed within each four-byte word. Hence **72 × 6 × 5 × 12 = 25,920 fully specified configurations**. A complete selected raw coupon is generated for each, XORed with the untouched recorded K04 mask and checked against the original unmodified K04 SHA256 commitment.

Source controls were fixed to five *intact, unselected* printer rows `[0,3,43,84,127]`, with their exact original full 16-byte payloads. This is a full-output source constraint, rather than fitting only a few bits or the selected copied payload.

## Executed results and positive control

```text
original printer source SHA pin OK; rows=133, source controls=[0, 3, 43, 84, 127]
keys=72 nonces=6 counter_forms=5 layouts=12 configurations=25920
original complete five-control source emitter fits=0; max simultaneous source controls=0/5
original commitment selected candidate hits=0, details=[]
planted known-family positive: five-control fits=1, target matches=1
```

The synthetic positive constructs all five control packets and selected full coupon from configuration `(keyindex=3, nonceform=4, counterform=2, layout=7)` in the same family, then identifies that source model and the corresponding masked component **once**. The source-hash check, row selector check, fixed keys/nonce forms, source fit and full original K04 digest test all completed locally on the original 46-file ZIP without editing evidence.

Portable reproduction: [`agents/agent47/k04_chacha20_sourcekey_counter_sft.py`](../agents/agent47/k04_chacha20_sourcekey_counter_sft.py). Python 3 + `cryptography>=46`; run with repository `resources/` and original `resources/candidate.json`. The portable version reads the live original acceptance/route values and six accepted source components, and embeds no replacement commitments. External primitive definition: [IETF RFC 8439](https://datatracker.ietf.org/doc/rfc8439/) and [cryptography ChaCha20 API](https://github.com/pyca/cryptography/blob/main/docs/hazmat/primitives/symmetric-encryption.rst).

## Conclusion and next decision

The tested 25,920 source-derived ChaCha event emitters cannot explain even one of the five source-control packets, and none predicts an accepted K04 component. This **does not** exclude ChaCha with an unknown hardware-held secret key, alternate source key derivation, different nonce schedule, real printer firmware, or an independently authenticated physical print. The result supplies zero new selected coupon bits. Blindly expanding cipher and key dictionaries without a source-identified emitter would repeat a weak strategy. Recovery remains K01/K02/K03/K05/K06/K07 PASS; K04/K08 unknown and combined REC8 INCOMPLETE. Research priority remains a source-specific selected-stage model or exact author-final K08 text.
