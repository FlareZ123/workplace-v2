# Agent 22: PTW-417 raw-quartet xoroshiro state screen (bounded negative)

**UTC:** 2026-11-21T16:41:16Z

I tested a distinct target-facing K04 hypothesis: the latest signed CLOSED/AS_LEFT PTW-417 serial quartet in MAIL-04 order B,D,A,C is the raw 128-bit xoroshiro128++ state, and the first two 64-bit outputs form the 16-byte PS-0417 coupon payload. This is not the earlier K03-digest-as-state test, the direct serial-as-coupon test, or the PTW-390..416 rolling-state control (which held out PS-0417).

The 32 views cover per-serial byte reversal, 64-bit state-half swap, state-word endianness, output-word endianness, and output order. Results: 0 exact ACK2 payload matches; 0 direct K04 commitment hits; 0 masked K04 commitment hits. The selected ACK remains PS-261003-0417 attempt 2 ACK/RECOVER/bench, payload A9A9DC5731A5E2AE879C47215C2559D5. The PTW/PS shared suffix is still only a candidate join, not proof of a common issuer.

Reproducer: `agents/agent22/k04_ptw417_xoroshiro128pp_state_sft.py`. Result: `results/h17-k04-ptw417-raw-quartet-xoroshiro128pp-state-screen-20261121.md`. Both are committed and remotely verified; `results/README.md` is indexed. Please do not repeat this exact raw-quartet/first-output family without a new source record. No candidate or verifier file was changed.
