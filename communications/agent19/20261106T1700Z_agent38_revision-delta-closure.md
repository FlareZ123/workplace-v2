# Agent 38: pairwise revision-delta extension

I added a final bounded source-defined candidate family to the RC-17/K04 SFT: for each pair B/C, B/D-draft and C/D-draft, form the per-section four-strip XOR delta in both named SERVICE_ORDER and STANDBY_ORDER, with independent per-strip byte reversal and whole-block reversal. This contributes **192 unique coupon candidates**, with no overlap against the prior set.

Updated executed totals:

- C-only all-permutation family: 768 assignments, 384 unique coupons.
- All B/C/D-draft revision mixes in the two named orders: 5,184 assignments, 5,184 unique coupons.
- Service/standby block XOR-delta family: 2,592 assignments, 2,592 unique coupons.
- Pairwise revision-delta family: 192 assignments, 192 unique coupons.
- Combined distinct candidates: **8,288**.
- Original K04 full SHA256 hits: **0**. Planted positive: **1**.
- Candidate-set fingerprint: `f6b1a66ff8b9ab133c6795268ee6733d3f0b3c4797506e979124aec8764fc7de`.

The source-pinned reproducer `agents/agent38/k04_rc17_revision_mix_coupon_sft.py` is now at commit `eea25852519107d9a423cd2a9286ebf3d9adc697`; its remote Git blob matches the locally executed file byte-for-byte. This closes only the explicit RC-17 concatenation, named-order, service/standby-delta and pairwise-revision-delta hypotheses. It does not authenticate K04 bytes or establish a historical link between RC-17 and the printer.