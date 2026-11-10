# H-17 K04: exhaustive source-derived stage −1082 rank-28 complete-coupon scan

**Agent 26 | 10 November 2026 | 268,435,456 complete original K04 candidates, zero accepted.**

## New finite target reconstruction

The 10 November [Agent7 whole-stage quotient spectrum](h17-k04-native-stage-relocation-rank-gap-20261110.md) identifies **−1082** as the only four-native-word MT stage with **28 remaining independent source bits** in the full −1100..1037 scan. Earlier original-target native-stage relocation enumerated only ranks **0..4** and found zero authentic K04 coupon matches. Thus stage −1082 is a distinct, previously untested **finite complete-coupon family**, rather than a duplicated low-rank scan.

The historical printer source remains the original unchanged `resources/evidence/print/spool-reconstruction.log`, pinned SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. Exactly 132 intact full 16byte payloads are fitted to Agent49's **conditional**, historically unverified native MT19937 p951 start-index geometry; selected row129, the damaged ESC-N / PS-261003-0417 / RECOVER / attempt2 ACK, is excluded **before any hex decode**. Source GF(2) rank = **15,365**.

For each native state bit at the fourword stage −1082, reduce its 19,968-bit symbolic expression by the source basis, yielding an observed constant plus a residual vector over source-free state coordinates. Transposing these 128 residuals gives exactly **28 independent complete-coupon directions**. Temper each 32bit word with the original hypothesis's MT output tempering and serialize as original printer little-endian 32bit words. The all-free-zero projected coupon base is:

`020000000296C31CC1ABD694A9C9EAE2`

All **2^28** possible fourword printer coupons consistent with the entire surviving printer source under this stage hypothesis are obtained by XORing 28 independent 16byte directions. XOR each coupon with the unmodified route mask `8556C8CB6140A7F9A5123AC7571BEE1C`, SHA256 the entire resulting 16bytes, and compare the entire unchanged official K04 target `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`.

## Completed computation

The original local read-only run constructed rank15,365 and rank28 from the source, emitted the affine coupon base/directions, then enumerated all **268,435,456** complete candidates by a Gray-code flip of one precomputed 16byte direction at each step. The corresponding C++17/OpenSSL SHA256 scanner with OpenMP eight requested threads and four effective CPU cores completed the full historical search in **55.101 seconds**, reporting:

```text
SYNTHETIC_POSITIVE full complete coupon at Gray-index 1337 recovered exactly once in 65536
ORIGINAL_RANK28_DIRECT done total=268435456 original_hits=0 planted_hits=1 seconds=55.101
```

The planted digest is independently computed from a complete stage−1082 coupon at Gray index1337, then recovered exactly once, exercising the same full packet, mask and complete digest path. The original comparison was never replaced by the planted digest. A simple, pure-standard-library full source-to-target SFT [`agents/agent26/k04_rank28_stage_fullscan_sft.py`](../agents/agent26/k04_rank28_stage_fullscan_sft.py) regenerates the precise 28 affine directions from Agent49's pinned source reader and performs the exact 2^28 tests. The local accelerated C++ calculation used the same generated base and 28 independent vectors. This artifact is reproducible without preserving a huge brute-force output corpus.

## Scope and decision

**Zero authentic K04 hits** for this exact conditional fourword stage −1082 and ordinary printer serializer. The result rules out this single native producer-stage **under the conditional p951 geometry**. It does not establish that stage −1082 ever issued the physical 18:02 ESC-N coupon; this stage precedes the ordinary retained print chronology and has no source-authenticated selected-stage bridge. Alternate per-word byte layouts, other high-rank stages, independent producer state, and unknown physical-copy corruption are outside this test.

This contributes a new full-coupon elimination without claiming an authentic recovered byte. Original K01/K02/K03/K05/K06/K07 remain six individual PASS; K04 and K08 remain MISSING; REC8/1 combined remains INCOMPLETE. No original evidence, routing, verifier, commitments or canonical `candidate.json` was changed.
