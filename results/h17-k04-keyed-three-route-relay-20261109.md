# K04: keyed three-route relay with an independent whole-coupon control

**9 November 2026, Agent 17. Original H-17 source-only experiment. No K04 acceptance.**

## Complete-value reconstruction hypothesis

Treat the three route-mapped late ACK print objects as outputs of a shared keyed issuer followed by a fixed unknown 16-byte XOR printer/copy pad. For a source-described route object *r*, set

`P(r) = issuer(key, serialize(route metadata)) XOR pad`.

Calibrate `pad` from the complete preserved ESC-S source ACK at 18:24, withhold the independent complete WATCH-SPARE source ACK at 18:25, and predict it before interpreting K04. Then predict an entire ESC-N coupon for the selected 18:02 ACK2 event and reduce it using the untouched official K04 mask and original 256-bit commitment. **The copied selected ACK payload is never used to fit any model or create a target candidate.**

The actual producer is not identified by the source. This is exploratory. It extends the earlier [cross-slot direct HMAC emitter](h17-k04-crossslot-hmac-perjob-producer.md) by introducing a nuisance pad eliminated through **two distinct complete historical late-ACK routes**. It differs from Agent 17's earlier unkeyed two-anchor digest-to-GF128 affine fit, which had no third historical complete coupon. The source return register provides job-to-lane/account/filing mappings, but does not attest common issuer firmware or physical paper integrity for either preserved source object.

## Frozen original inputs

- North selected: ESC-N, job `PS-261003-0417`, ACK attempt 2 at 18:02 UTC. Its copied payload is excluded.
- South calibrator: ESC-S, job `PS-261003-0448`, ACK attempt 1 at 18:24 UTC, preserved payload `234BE186E97EE05830909790E336109E`.
- Watch blind control: WATCH-SPARE, job `PS-261003-0420`, ACK attempt 2 at 18:25 UTC, preserved payload `432475F72A62DB39F3D5693E2C937FA4`.
- Original printer file SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`; original recovery-routing SHA256 `f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5`.
- Eight candidate 16-byte keys: the six untouched accepted component values, route K04 mask, and K08 nonce. All six accepted component SHA256 values are verified against original acceptance.

## Fixed candidate mechanisms and results

Twenty source-defined metadata field collections cover job ID or suffix, route, return set, account, filing reference, timestamp/date, attempt, class and destination. Cross them with five separators, six literal domain prefixes, two field orders, and original/uppercase text. Use seven keyed digest issuers: HMAC-SHA256, HMAC-SHA512, keyed BLAKE2s, keyed BLAKE2b, SHA256(key||message), SHA256(message||key), and SHAKE128(key||message). Use first/last 16 digest bytes, native or reversed. One unknown shared 128-bit XOR pad is eliminated from the south output per complete model.

| Actual test | Result |
| --- | ---: |
| Complete source-model combinations | **537,600** |
| Exact full-128-bit WATCH-SPARE historical reproductions | **0** |
| Complete original K04 component SHA256 hits | **0** |
| Independently planted complete withheld north coupon controls | **28/28 PASS** |

The full original test ran locally against the user-supplied 46-file archive with the same source metadata and candidate algorithm. No selected ACK2 bytes were used for source calibration; the code uses only target job metadata. The [portable source SFT](../agents/agent17/k04_keyed_three_route_relay_sft.py) preserves the finite issuer and serializer vocabulary, checks source digests, checks all six trusted key digests, executes all 537,600 candidate reductions, and recovers every synthetic hidden north coupon under all seven issuers and four presentations. This is a bounded mechanism exclusion, not a globally exhaustive source model.

**Conclusion:** A common fixed-XOR-pad printer relay using any of these specific source keys, metadata representations and digest forms is incompatible with the complete preserved watch historical coupon, and none predicts the accepted K04 value. This supplies no newly authenticated K04 coupon bits. The six original accepted REC8 components are unchanged; K04, K08 and combined acceptance remain unresolved. Further work requires a different source-visible issuer/copy-stage mechanism, rather than broadening this failing arbitrary metadata list without a discriminator.
