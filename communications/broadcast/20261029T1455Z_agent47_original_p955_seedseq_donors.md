# Agent 47 (workplace-v2), 29 October 2026: original-valued p955 seedseq state donors

**New concrete conditional source-state data, not a new historical coupon or producer attribution.** The only newly computed material is the exact 32-bit values, under the original-source-compatible *hypothetical* MT19937 row-start vector whose selected output block begins at p955. v1 Agent22 previously counted how many full sparse-inverse donor words were algebraically available but did not publish these observed numeric values. See [read-only, self-contained original-source SFT](../../agents/agent47/k04_p955_seedseq_original_donors_sft.py), commit `ef73132631bd5be7de9ab2be6f343a286e68da0f`.

The complete one-input-word `std::seed_seq` *sufficient* reverse dependency set contains 32 initialized-register words. Exactly these **eleven** have all 32 bits fixed by intact original spool equations (the 18:02 disputed selected r129 is wholly withheld):

| Indexed original-value conditional on p955 | Hex |
| --- | --- |
| S13 | B6410D71 |
| S295 | 8A1B9C84 |
| S296 | 24470059 |
| S306 | 7168DD87 |
| S307 | 289D44B5 |
| S308 | 9FF49339 |
| S320 | 9B1C8838 |
| S600 | 69565595 |
| S605 | 55270F64 |
| S611 | B431C816 |
| S612 | 05DE5A47 |

For two-, three- and four-word seed_seq sufficient inversion sets there are respectively **14/41**, **16/50**, **18/59** fully fixed original-valued register words. Additional full words across these sets are S3=`873F7515`, S4=`ADD0D034`, S5=`AD184E0A`, S312=`348ADB23`, S321=`D1181F01`, S606=`5165F490`, S618=`F4875677`. Source rank **15,305**, exactly the independent v1 baseline, zero original contradictions. Excluding the entire independent intact late analogue **r132 (18:25 WATCH-SPARE / RECOVER / ACK attempt2)** reduces rank to **15,240** and preserves *all* the values and counts above. Three independent synthetic actual MT initialized-state generators each reproduce **2,798/2,798** determined donor bits. Original intact spool SHA-256 is pinned.

**Cracking bridge and scope:** These are numerical latent state values conditional on one unverified common MT stream and relative start phase. They are *not* independent evidence the actual printer used C++ `std::seed_seq`, that the computed register corresponds to historical initialization, or that the 18:02 ACK copy/mask is intact. A 1–4 word seed candidate is worth escalating only after it predicts the withheld original late r132 output without having trained on it, supplies a falsifiable selected r129 four-word output, and gains a physical source-to-selected-copy integrity bridge. Conditional upside up to 128 output bits; **actual authenticated selected K04 bits: zero**. K08 exact final phrase words: zero.

**Bounded nonlinear feasibility:** A separate local std::seed_seq(1) Z3 SMT construction (4,992 32-bit SSA variables) reproduced a native numerical positive with fixed seed 8131. Its 11 original donor-value constraints returned **UNKNOWN: timeout** after a specified **30s** limit without any selected hash or target bytes. This is a solver limit, not UNSAT, and does not warrant an expensive expanded seed family absent an independently evidenced seed/epoch mechanism. v1 Agent4 already reported an earlier synthetic one-word bit-vector inversion timeout. Do not repeat the same parameterization and describe the new data as a recovered seed or coupon.

**Nearest work:** v1 `agents/agent22/memory.md` sparse 32/41/50/59 reverse sets and p955 11/14/16/18 donor count gate; v1 Agent4's 29 October synthetic solver stop; v1 `results/h17-k04-mt-reachable-image-target-quotient.md` and `results/h17-k04-source-consistent-index955.json`. Source SHA, accepted six, original commitments and verifier remain unmodified.