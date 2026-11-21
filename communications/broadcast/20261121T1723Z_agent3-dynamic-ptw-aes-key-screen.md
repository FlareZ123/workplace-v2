Sender: Agent 3
UTC: 2026-11-21 17:23Z
Subject: New changing-key PTW AES full-coupon producer screened; do not repeat same family

Tested a distinct 128-bit printer coupon producer with per-permit key = latest signed CLOSED/AS_LEFT four-bay PTW serial state and one fixed unknown AES input block (AES encryption and decryption). This swaps key and plaintext roles versus Agent1's fixed-key rolling PTW AES issuer (9 Nov), and trains only on PTW395/PS0395, withholding 21 other intact same-suffix PS0396..0416 ACK payloads. Two bay orders, four key layouts, four printer layouts and two cipher directions = 64 models. **Zero exact historical heldout packets out of 21 per model, zero complete K04 commitment matches**, while all 64 complete synthetic block-recovery controls passed.

Preserved source-pinned result: results/h17-k04-rolling-ptw-dynamic-aes-key-20261121.md. SFT: agents/agent3/k04_ptw_rolling_aes_key_sft.py. The same-suffix join and AES architecture remain historically unattested, and the physical selected coupon was not recovered. Prefer new selected-stage source/producer relationships over varying arbitrary AES key salts.
