# K04: cross-component HMAC-SHA256 coupon producer, source-calibrated original test

**Agent 18, 3 November 2026. Original K04 commitment NO_MATCH.** The six previously accepted slots remain unchanged, and both missing components remain unresolved.

## Mechanism and source premise

The original archive's six independently validated components might plausibly have served as cryptographic keys in a *per-print-job HMAC-SHA256 producer*. Such a generator could issue a different 16-byte coupon for every job/attempt using a job identifier, timestamp, class, destination and state as message data, independent of the hypothesized long-lived MT stream. **No surviving company document identifies this producer or connects the six components to a printer HMAC key.** This is a finite direct-complete-coupon exploratory test, rather than an assertion of original firmware.

Prior [Agent9 unkeyed metadata hash/XOR-pad study](../agents/agent9/k04_metadata_generators_sft.py) covered unkeyed metadata digests, simple shared XOR/add pads and per-record scalar PRNG seeds. The mechanism here uses **authentic 16-byte components as secret HMAC keys** and directly predicts intact original coupon bytes without fitting a pad.

## Frozen source-calibrated family

Keys: six accepted original K01, K02, K03, K05, K06, K07 16-byte components plus the original 16-byte K04 route mask and K08 desk nonce (eight bytestring keys). Each key has independently source-accepted or route-sheet provenance but no historically attested printing role.

For each original print job, generate 30 deterministic metadata representations: job identifier or suffix, attempt number, printer class/destination/state, original ISO timestamp, various colon/pipe joins and two canonical compact JSON serializations. Each representation is also checked with six literal domain prefixes `""`, `"K04|"`, `"H17|"`, `"REC8|"`, `"ESC-N|"` and `"H-17/"`, yielding **180 messages per row**. Evaluate HMAC-SHA256 and extract either first16 or last16 digest bytes. The original selected 18:02 ACK2 packet is withheld from the **132 intact packet source-replay checks**, which use exact full 128bit equality. The selected event's metadata is then independently hashed with the same rule to generate a complete hypothetical K04 component using the original route XOR mask and original SHA256 acceptance commitment.

| Test | Actual |
| --- | ---: |
| Original source printer controls | 132 |
| Accepted component/configuration key candidates | 8 |
| Metadata message representations per job | 180 |
| HMAC digest half views | 2 |
| Complete intact-source 128bit replay checks | **380,160** |
| Intact original source payload hits | **0** |
| Full selected-event K04 candidate checks | **2,880** |
| Original K04 commitment hits | **0** |

The [single-file source-pinned Python SFT](../agents/agent18/k04_hmac_perjob_sft.py) authenticates original spool SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`, selected row metadata and all six original accepted input hashes. A planted independent 128-bit HMAC key generates synthetic 132-record calibration packets and a withheld row. All named source controls reproduce exactly, and the withheld synthetic payload passes the full original-mask/XOR/SHA256 simulated acceptance path. The original source and commitment branches yield zero hits.

## Scope and value

This newly tested HMAC producer family fails **both** its complete-packet source calibration and the actual missing K04 commitment. Its negative covers only the eight chosen keys, 180 job-message formats and first/last digest halves; it cannot rule out a non-exported secret, different KDF, unrelated printer firmware, extra salt, long-stream PRNG or original print-medium copy fault. It supplies no authenticated coupon bit or final Emily phrase.

Original `resources/`, route, acceptance and verifier remain unchanged. REC8/1 retains **K01/K02/K03/K05/K06/K07 PASS; K04/K08 MISSING; combined INCOMPLETE**.
