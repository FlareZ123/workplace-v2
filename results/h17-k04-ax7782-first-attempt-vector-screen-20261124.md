# AX-7782 first-attempt checkpoint vector as a K04 cross-slot candidate (2026-11-24)

**Agent 10.** Bounded source-derived exploratory negative. No K04 candidate recovered.

## Source basis and positive control

MAIL-13 says AX-7782 is the final custodian handoff, that there are eight chunks numbered 0–7, and that each chunk was retried once; the second attempt is the checkpoint used in the committed chain. It also says to order by chunk sequence and preserve the short checkpoint fields as bytes, including leading zeroes.

The exact transfer audit is `resources/evidence/transfers/transfer-audit.jsonl`. Selecting AX-7782's attempt-1 checkpoint for each seq 0..7 gives the alternate 16-byte vector:

```
62244DFBF3B8CA3D1888F22A3DB08769
```

The source-defined K07 positive control uses attempt 2 for each seq 0..7:

```
8947CEDCB9CC73BAB7E87BE63302C5C9
```

Applying the published K07 rule (SHA-256, first 16 bytes) to the attempt-2 vector gives `93495F5E425AB8E592123DABAEB68545`, whose SHA-256 matches the original K07 commitment. This validates the transfer selection, byte parsing and sequence order used here.

## Hypothesis and frozen candidate family

The attempt-1 chain is the only other complete 16-byte checkpoint vector for the selected handoff. I tested whether it could be a K04 component or an opaque K04 payload, and whether the retry relation itself could provide that 16-byte object. This is an exploratory AX→K04 cross-slot hypothesis; MAIL-13 does **not** state that transfer checkpoints are printer coupons.

The direct candidate family comprised the attempt-1 vector, attempt-2 vector, and per-byte XOR retry delta, each under six byte layouts: raw, full reversal, reversal of the eight 2-byte chunks, byte-swap within each 2-byte checkpoint, both chunk reversal and byte-swap, and reversal of 4-byte words. Each was tested directly and XORed with one of four 16-byte operands: zero, the official K04 route mask, the PS-0417 attempt-2 RECOVER ACK payload, and mask XOR that ACK payload. **72 complete component candidates** were checked against the unchanged full K04 SHA-256 commitment.

A separate small family checked SHA-256 first-16-byte outputs over the transformed attempt-1/attempt-2/delta vectors, concatenated attempts in both orders, and bytewise modular add/subtract retry combinations, each directly and after the K04 mask. **48 additional complete candidates** were checked.

## Result

**Zero of 120 candidates match K04.** The first-attempt vector itself and its official-mask XOR both miss. The attempt-2 vector remains the validated K07 source input; it does not produce K04 under the tested direct/hash constructions.

## Scope

This is distinct from the previously recorded per-chunk retry-delta-vector screen and from the AX checkpoint-to-MT donor/interleave models: it tests the complete first-attempt vector and a small frozen family of direct component constructions. It does not establish a historical AX-7782→PS-0417 dependency and does not exclude other source-defined checkpoint transforms. K04's stated source route remains the ESC-N PS-0417 RECOVER payload XOR the recorded mask; the transfer audit is only an exploratory cross-slot source.

No original evidence, route, acceptance commitment, verifier or candidate was changed. K04 and K08 remain unrecovered.
