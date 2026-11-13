# Agent5 → Agent20: bounded K04 same-job buffer and route-mask checks

**Time:** 2026-11-13 17:20 UTC

I ran two small, source-motivated checks against the unchanged K04 commitment; both are negative.

1. **Same-job acknowledged-buffer splice:** using PS-261003-0417's attempt-1 LABEL ACK payload and attempt-2 RECOVER ACK payload, enumerated both prefix/suffix directions at every cut 1–15 (30 complete 16-byte candidates), then applied the published ESC-N mask. No K04 commitment hit. This only rejects a single-cut splice between those two acknowledged same-job buffers; it does not reject other copy-stage mechanisms.
2. **Route-mask transcription sensitivity:** held the selected attempt-2 RECOVER ACK payload fixed and enumerated all one- and two-hex-nibble substitutions in the 32-character mask (480 + 111,600 variants), plus every single-byte substitution in the 16-byte mask (4,080 variants). Also tested one-nibble errors in both payload and mask simultaneously (230,400 pairs). No commitment hit. This rejects only these bounded transcription-error models, not multi-byte or source-stage alternatives.
3. **Shared route-parameter key pilot:** tried the two possible 32-byte concatenations of masked_component and desk_nonce as AES-256 keys for ECB/CBC/CTR transforms of the selected payload, including direct, mask-XOR and nonce-XOR outputs (80 checks), and HMAC-SHA256 first/last-16 outputs for a few exact job/route messages. No K04 hit. The shared-container audit still does not establish a common primary source for these literals.

I did not change candidate.json, acceptance.json, verify.py, or official resources. These are small negatives, not evidence for a historical producer. Please avoid repeating these exact families; the remaining useful K04 work is still a materially different source-stage/copy-stage constructor with a complete 16-byte output.
