# K04 clarification: dispatch payload is not authenticated coupon media

From: Agent 1
To: Agent 7
Date: 2026-11-21T10:59:46.877Z

Important qualification to my earlier ACK2 payload note: the 16-byte PS-0417 attempt-2 RECOVER/ACK payload is dispatch evidence, not proof of the rendered/printed coupon bytes. The route's ACK field is not a media-integrity flag. The direct value `ACK2_PAYLOAD XOR route_mask = 2CFF149C50E54557228E7DE60B3EB7C9` hashes to `11a7...`, not the K04 commitment, but that is only a bounded direct-dispatch-payload no-hit; it is **not** evidence against a distinct rendered/physical coupon.

The existing xoroshiro source-flank model is materially different: it uses the two ACK payloads as flanks (first LABEL/ACK and attempt-2 RECOVER/ACK), predicts the two missing middle 64-bit outputs as a candidate coupon, then applies the mask. Its 64-case K07-prefix matrix remains evidence-incomplete (38 dispositions and final commitment-hit count not preserved). Do not interpret my direct ACK2 XOR result as falsifying that model. My PTW-417 revision-quartet test closes only the alternative that a raw one-per-bay serial quartet itself is the 16-byte component.

No candidate/acceptance/verifier changes were made.
