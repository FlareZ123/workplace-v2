# K04 selected physical coupon: AES-GCM/GMAC three-route source holdout

**Agent 2, 10 November 2026. Original K04 NO_MATCH.** Six prior REC8/1 slots remain individually PASS. K04 and K08 are missing; combined acceptance is INCOMPLETE.

## Proposed complete-value reconstruction mechanism

The three original RECOVER/ACK events represent north (historically selected ESC-N coupon), south (ESC-S), and WATCH-SPARE. A hypothetical common **AES-GCM issuer** emits a 16-byte authentication tag for source-recorded job, route, timestamp, cassette and role metadata. An unknown common 16-byte XOR transfer/copier pad is calibrated by the independent intact south ACK; the withheld intact WATCH-SPARE ACK must be predicted **in full** before the proposed issuer can generate an entire north physical coupon.

For each candidate model, calculate `T(route) = AES-GCM-tag(K, IV(route), plaintext(route), AAD(route))`. The hypothetical common copy pad is `pad = T(south) XOR actual_south_packet`. Demand `T(watch) XOR pad == actual_watch_packet`, using all 128 bits. Only a surviving model may propose `coupon = T(north) XOR pad`, then `K04 = coupon XOR original_route_mask`, and finally compare the unchanged full SHA256 K04 target. **The copied north-selected ACK2 payload is excluded entirely from fitting and target construction.**

AES-GCM with a routed metadata IV/AAD and transport XOR is a distinct issuer from the tested source-keyed HMAC, unkeyed digest, AES-CMAC, static block-AES and legacy PRNG models. The historical source does not attest GCM, a shared copier pad, a common printer firmware implementation, or integrity of the south/watch copied artifacts. This is an exploratory conditional mechanism, not producer attribution.

## Frozen source and candidate boundaries

Original print spool SHA256: `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`.

- North selected: PS-261003-0417 ESC-N, RECOVER ACK2 at 18:02 UTC, original recorded copied packet intentionally withheld.
- South calibration: PS-261003-0448 ESC-S, RECOVER ACK1 at 18:24 UTC, entire original copied packet `234BE186E97EE05830909790E336109E`.
- Watch whole blind control: PS-261003-0420 WATCH-SPARE, RECOVER ACK2 at 18:25 UTC, entire original copied packet `432475F72A62DB39F3D5693E2C937FA4`.
- Exact original K04 mask: `8556C8CB6140A7F9A5123AC7571BEE1C`; original K04 SHA256 target: `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`.

Candidate issuer keys: six independently accepted known 16-byte REC8 values (each checked by unchanged original commitments), original K08 desk nonce, original route mask, and three ordered 32-byte concatenations of known accepted values, **11** keys total. For each route use **10** fixed GCM 96-bit IV encodings (source job, job+attempt, route/job/attempt, event timestamp+job+attempt, timestamp/attempt packed in either byte order, job prefix/suffix, original nonce prefix/suffix). For both plaintext and AAD use **9** source-defined byte strings (empty, full job, route, cassette ID, job/attempt, job/class/destination, route/job/class/destination/attempt, timestamp, timestamp/job/attempt). This creates exactly `11 × 10 × 9 × 9 = 8,910` complete model assignments.

No source fields or digest values were changed. The 2025 property card and the disputed north copied bytes were not used for model selection.

## Executed original test and positive control

The read-only [one-file SFT](../agents/agent2/k04_gmac_three_route_sft.py) was run against the unchanged original ZIP extraction using Python `cryptography` AESGCM.

| Result | Count |
| --- | ---: |
| Entire south-calibrated source models | **8,910** |
| Models reproducing all 16 WATCH-SPARE original bytes | **0** |
| K04 commitment accepted | **0** |
| Synthetic planted full south/watch shared-pad control | **PASS** |

The synthetic positive constructs complete south and watch packets under one real AESGCM model, applies an independent 16-byte XOR pad, and exactly recovers that pad and the withheld watch packet. It tests the model operation, not the historical printer hardware. The original watch record fails complete prediction for all 8,910 historical key/IV/AAD/plaintext selections. Therefore this model has **no source-qualified complete north physical coupon** and supplies **zero** authentic K04 selected bits.

## Boundary and next recovery action

This excludes only the stated **source-carried key and original-metadata AES-GCM shared-XOR-pad issuer family**, subject to treating copied south and watch packets as faithful full-source controls. It cannot exclude a secret key, independent pads, unrelated printer firmware, different original source fields, different GCM framing, the actual physical selected coupon or any alternate paper-copy stage. The original K08 final author wording remains unquoted.

A genuinely productive follow-on would need an **independent complete historic printer/copy relationship with an observable event selector**, or the two actually indexed native gap blocks required by the conditional [K04 MT gap reconstructor](h17-k04-two-gap-conditional-exact-coupon-reconstructor-20261109.md). More arbitrary AES key expansion without an original publisher cue cannot identify a target packet.

The canonical `candidate.json`, original source ZIP, `resources/verify.py`, commitments and routing were left untouched.
