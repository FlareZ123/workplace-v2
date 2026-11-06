# K04 selected-coupon RFC UUIDv3/v5 issuer: 930,240 distinct complete coupons

**Agent 16 | 6 November 2026 00:04 UTC. Original K04: NO_MATCH.** This is one bounded alternative *selected physical issuer* model. K01/K02/K03/K05/K06/K07 remain accepted; K04/K08 are unresolved; combined recovery remains INCOMPLETE.

## Distinct causal hypothesis

The source selects one 16-byte coupon for printer route ESC-N / job `PS-261003-0417` / RECOVER ACK attempt 2, but the reconstructed copied buffer `A9A9DC5731A5E2AE879C47215C2559D5` fails the original commitment. An issuer may plausibly have printed a reproducible **name-based 128-bit UUID** derived from the archival job/route/name under RFC UUIDv3 (namespace + MD5) or UUIDv5 (namespace + SHA1). This would predict a *complete selected coupon* without assuming the copied bytes were authentic. No surviving original printer document attests a UUID issuer, so the hypothesis is speculative. It is distinct from fixed metadata SHA256 output, byte-lane-copy edits, and arbitrary PRNG seeds.

The original retained spool, route and archive-label source SHA256 are pinned in the [standard-library read-only SFT](../agents/agent16/k04_uuid_archival_name_sft.py); the actual 133 source packets, original K04 mask, original unmodified K04 SHA256 target, and accepted six other components are used directly. It does not read or change `candidate.json` or modify original evidence.

## Finite family and original execution

- **17 namespaces:** four RFC standard namespaces; the actual K04 mask and K08 desk nonce; six accepted source-reduced components; selected copied ACK; and four intact late printer request/ACK payloads.
- **5,472 distinct exact source-metadata names:** job ID/last suffix, ESC-N, envelope ID, event timestamp, event/attempt class and state, plus ordered two- and three-field serializations with nine separators and uppercase/lowercase variants.
- **Two UUID algorithms** (v3 and v5), five full 16-byte layouts (canonical, Windows/GUID mixed-endian, reverse bytes, reverse 4-byte lane order, reverse bytes inside each 4-byte lane).
- Apply the immutable mask as prescribed, SHA256 the resulting sixteen component bytes, and compare all 256 bits with the original K04 commitment.

The executed original ZIP test produced:

| Quantity | Original result |
| --- | ---: |
| Complete candidate assignments | 930,240 |
| Distinct 16-byte coupons | 930,240 |
| Original K04 commitment matches | **0** |
| Independently planted in-family full positive controls | **1 / 1** |
| Sorted-coupon-set SHA256 | `17d48310b006ea8ca5d276a265a06f263cd80667598d0a2d33a71179bf998df1` |

As an independent **source-only structural diagnostic**, among 132 intact unselected printer payloads only **4** have the RFC UUIDv3/v5 version-and-variant bit pattern in their direct layout, while 15 have it in *at least one* of the five layouts. The selected copied ACK2 has an incompatible version nibble. This is compatible with random data and contradicts a simple assertion that all 132 ordinary payloads are canonical RFC UUIDv3/v5 records. The selected physical original remains unauthenticated, so this diagnostic cannot rule out a special issuer used only for ACK2.

The SFT pins the original source hash, verifies the unique target selector, checks that the retained ACK+mask fails, enumerates exact UUID source constructions, and uses a planted RFC UUIDv5/mixed-endian sample that survives the whole mask/SHA256 path uniquely.

## Decision

Do not repeat this particular RFC UUIDv3/v5 name/namespace/layout campaign or treat the copied ACK version nibble as an authenticated property of the physical coupon. A different UUID version, an unknown namespace/name, non-UUID coupon producer, physical buffer corruption, or an independent end-to-end derivation is outside this finite test. **No original physical K04 bits, K08 final words, or additional REC8 PASS components were recovered.**
