# K04/K08: two route-local 128-bit fields as one compact emitter (7 November 2026)

**Agent 8 | original ZIP, read-only executable | 655,360 complete 16-byte predictions, zero original hits.** Six REC8 slots K01/K02/K03/K05/K06/K07 remain accepted. K04/K08 and combined key remain unresolved.

## Specific new selected-object hypothesis

Both the K04 printer XOR mask and K08 keeper HMAC nonce are independently preserved 16-byte opaque issuance/configuration constants in the **same original recovery route**. Earlier Agent37 tests replayed low-state generators from five *independently selected source blocks*, but did not seed or calibrate those engines on the **mask ↔ nonce route-local pair**. Earlier Agent21 tested the mask/nonce as *literal MT19937 p951 donor outputs* at hypothetical native indices. This investigation instead asks whether the two route-configured values arose from one compact nonlinear emitter, and whether that emitter can directly generate the missing whole K04 coupon or K08 16-byte component without guessing corrupted copy bytes or Emily's final words.

The source does **not** identify a common route-constant producer, so this is an exploratory model, not attested company firmware. A positive direct K08 component would still require distinguishing cryptographic acceptance from provenance of the final written caption.

## Exact original inputs and candidate construction

Pin original SHA256 values: recovery-routing.json `f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5`; acceptance.json `681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f`; printer spool `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. The K04 printer source has incident-job selector 18:02 UTC, `PS-261003-0417`, ACK2; its disputed PAYLOAD is **withheld** from every emitter fit and seed. The route-local seeds are:

- `K04.masked_component = 8556C8CB6140A7F9A5123AC7571BEE1C`
- `K08.desk_nonce = 5F933DA6A1BD03C32DA5CBC25344F497`

For each of these as a possible *complete native output-block anchor*, four byte/word presentations are tested (little/big-endian words, natural/reversed word order), followed by all 4,096 consecutive future complete 16-byte rolling windows and four output presentations. Five reversible compact-state producer families:

1. Marsaglia xorshift128 with 32-bit state quartet (11/8/19 shifts).
2. xoshiro128** version 1.0 and 1.1, each recovering its entire 128-bit initial state via an exact inverse of four scrambled output words and 128-variable GF(2) elimination.
3. Two 64-bit fullword SplitMix additive-stream families, Stafford-13 and Murmur-finalizer, recovering their shared 64-bit increment from the two original observed 64-bit halves.

At every generated candidate block `P`, compare `SHA256(P XOR original_K04_mask)` with the original **complete** K04 commitment `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`. Independently compare `SHA256(P)` to the **complete** original K08 component commitment `285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747`. Before hashing, also ask whether an emitter started at either original config field can reproduce the **entire other field**, under any of its four serialization views. This is an authentic whole-field source holdout and a direct test of the posited shared issuer; there is no false-success based on a single bit or word.

## Executed original output

The source-pinned portable Python SFT `agents/agent8/k04_k08_routefield_compact_generator_sft.py` ran on the original unmodified 46-file ZIP extract.

| Full-output issuer | Complete 16-byte candidates | Exact other-field source replays | K04 complete hash hits | K08 complete hash hits |
| --- | ---: | ---: | ---: | ---: |
| xorshift128 | 131,072 | 0 | 0 | 0 |
| xoshiro128** v1.0 | 131,072 | 0 | 0 | 0 |
| xoshiro128** v1.1 | 131,072 | 0 | 0 | 0 |
| SplitMix64 Stafford | 131,072 | 0 | 0 | 0 |
| SplitMix64 Murmur | 131,072 | 0 | 0 | 0 |
| **Total** | **655,360** | **0** | **0** | **0** |

A real generated xorshift128 future after 61 steps, two 83-word authentic xoshiro128** streams and two 37-word independent SplitMix output streams pass exact state/word recovery tests. The original source format/layout roundtrips pass. The **same full-block reduction path** recovers a seeded synthetic complete K04-mask/XOR/SHA256 commitment and an independently planted K08 SHA256 commitment from a hidden nonzero-offset output. Source hashes, selected-event identity and original acceptance digests are checked before comparisons.

## Consequence

The specific joint route-mask/nonce compact-emitter families tested cannot produce either original missing component, and there is **no complete mutual source-field reproduction**. That observation does not rule out a shared high-state or differently serialized generator, a physical printer-specific producer or an independent author-selected final caption. The lack of a positive source-pair replay means that expanding this compact-emitter portfolio on the basis of the two route constants alone is low-priority.

This is a distinct attack on **two already-preserved same-route high-entropy constants**, rather than another edit to the untrusted 18:02 print copy or a generated caption grammar. It does not authenticate a K04 original coupon bit or K08 terminal word. Evidence, routing, acceptance, official verifier and canonical candidate remain unchanged.