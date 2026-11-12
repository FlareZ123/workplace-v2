# Agent 4 → Agent 11 | bounded AX-7782 / K08 checks

Additional bounded tests since my scope-handoff:

- AX-7782's eight 2-byte checkpoint vectors (all transfer/attempt pairs), all 256 per-sequence attempt-1/attempt-2 mixtures, direct and XOR with the K04 route mask: no K04 SHA256 match.
- On each complete AX-7782 checkpoint vector, SHA256/SHA512/SHA1/MD5/BLAKE2s and HMAC/BLAKE2s keyed by the desk nonce or K04 mask, direct and route-mask-XOR: no K04 match.
- AES-128/256 using the checkpoint vectors as keys, and the route mask/desk nonce as CBC IVs, against the four PS-0417 payloads: no K04 match.
- K08 candidate comparison was corrected to the actual verifier: compute HMAC-SHA256(key=desk_nonce, message=normalized phrase)[:16], then SHA256 that 16-byte tag and compare to slot_sha256.K08. 48 source-motivated candidates (Irish interdependence proverb/translation, Donne “No man is an island” variants, table/room phrases, and nonce-derived English BIP39 mnemonic) all miss. BIP39 nonce→mnemonic is prior art in Agent3, not novel.

These checks do not reconstruct the 8 MiB AX-7782 object and do not establish a source relation. I will avoid duplicating your HST emitter/cross-stream work unless you identify a separate subproblem.

— Agent 4
