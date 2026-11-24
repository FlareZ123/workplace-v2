# PS-0417 ESC-N cross-slot ciphertext screen for K08 (2026-11-24)

**Agent 10.** This is a bounded negative result from the retained export. It does not recover K08 and does not establish that the reconstructed spool payload is authentic.

## Source basis

- `resources/evidence/h17-supplemental-office-files/print-fleet-retirement-note.txt` maps `PS-261003-0417` to `FA-17 / L-29/N / ESC-N`.
- `resources/evidence/mail/16.eml` says ESC-S is not an input to the keeper's desk phrase. This leaves ESC-N as a possible route, but does **not** establish that ESC-N is an input to K08.
- `resources/evidence/print/spool-reconstruction.log` retains four rows for the exact job:

| Attempt | State | Class | 16-byte payload |
|---:|---|---|---|
| 1 | ACK | LABEL | `E1E60D5F6B6DD2225FA6D5A2A63AD932` |
| 1 | REQUESTED | RECOVER | `CD3E4F216ADB2FB180DA2AA90B33F7A4` |
| 2 | ACK | RECOVER | `A9A9DC5731A5E2AE879C47215C2559D5` |
| 3 | REQUESTED | RECOVER | `44D53DFC29D7943A95D89371DA58EC64` |

- `resources/evidence/recovery-routing.json` specifies K08 normalization and HMAC-SHA256 with desk nonce `5F933DA6A1BD03C32DA5CBC25344F497` as key, retaining the first 16 bytes.
- `resources/acceptance.json` gives the K08 component commitment `285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747`.

## Hypothesis and frozen test

Because the K08 phrase is a keeper-envelope caption and the retained job has both a LABEL ACK and a RECOVER ACK on the ESC-N route, I tested whether either ACK payload or their ordered combination could be a ciphertext carrier for the phrase. This is an exploratory cross-slot hypothesis, not a source-established rule.

The test:

1. Used the two ACK payloads separately and concatenated in both orders. REQUESTED rows were controls, not treated as acknowledged output.
2. Tried AES-128 decryption with the desk nonce, the K04 route mask, and each accepted component K01/K02/K03/K05/K06/K07 as keys; modes were ECB, CBC, and CTR. CBC/CTR IVs were zero, desk nonce, or K04 route mask.
3. Applied bounded terminator/padding removal (NUL, space, PKCS#7) and the official K08 normalization, then recomputed HMAC16 and SHA-256 commitment.
4. Separately tested RC4 with the desk nonce as key and drop counts 0, 256, 768, 1024, and 1536; also tested XOR of the same-job payload sequences with the nonce, route mask, and accepted component keys.
5. Checked the raw LABEL ACK payload and its XOR with those known 16-byte keys as direct K08 component candidates.

## Result

**Zero K08 commitment hits.** None of the tested AES or RC4 plaintext candidates produced readable ASCII, and none of the normalized candidates matched the K08 commitment. The direct LABEL-payload component candidates and the bounded XOR candidates also missed.

## Scope and next useful action

This closes only the tested ESC-N payload/cipher/key/mode/sequence combinations. It does **not** exclude a different native spool representation, a different encoding, a missing source-sidecar, or a phrase on the original keeper-envelope face/margin. In particular, the spool log is a reconstruction: an ACK establishes receipt, not payload correctness. Do not promote any of these payloads to an authenticated K08 source.

The highest-value next K08 input remains a surviving native copy of the keeper-envelope face/margin or the authenticated photo-caption/profile sidecar that contains the exact final wording. No candidate, route, acceptance commitment, or verifier was changed.
