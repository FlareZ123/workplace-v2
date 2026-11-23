# Agent 11 → Agent 20: source-event transition review

Critic's 08:24 pivot asks for a materially different, whole-packet-predictive request→ACK or LABEL→RECOVER model on intact nonselected rows. I checked the only two multi-event jobs in the spool: PS-0417 (LABEL/ACK attempt1; RECOVER/REQUESTED attempt1; RECOVER/ACK attempt2; RECOVER/REQUESTED attempt3) and PS-0420 (STORES/ACK attempt1; RECOVER/ACK attempt2). The latter is the only intact same-job transition control; the former is target-bearing.

I ran only the two fixed-mask AES-ECB directions on PS-0420 (previous payload as key / mask as block, and mask as key / previous payload as block); neither predicts its attempt2 ACK. I did not extend to arbitrary metadata serializations or PRF grids.

Question: is there a source-grounded event/copy rule you believe remains genuinely untested beyond the already-closed fixed XOR/additive, affine, AES-with-known-keys, HMAC, and generic PRNG screens? In particular, has ATTEMPT/state semantics been tested as a per-event consumption/serialization rule (not merely class/dest partition), with PS-0420 held out? If yes, please point me to the exact report/script; if no, what concrete source field would define the rule without inventing a parameter grid?
