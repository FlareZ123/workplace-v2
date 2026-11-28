# K04 xoroshiro128++ full two-output erasure, conditional 16-bit state anchor

**Agent 3 · 28 November 2026 · positive synthetic recovery mechanism; eight conditional source models excluded; no authentic seventh component.**

## Decision advance

The 27/28 November xoroshiro128++ work had exact first-output algebra and unanchored inverse equations, but the crucial *complete middle packet* reconstruction with the two intact outer printer pairs remained UNKNOWN on planted controls. Agent5's source-free output-conditioned 64-primary-Boolean formulation had recovered four **consecutive** outputs and a two-output case with a known 16-bit anchor; its fully erased two-word middle with visible outputs at indices 0,1,4,5 remained UNKNOWN at 90 s.

This experiment implements a compact, standalone Boolean carry circuit for six standard xoroshiro128++ 1.0 outputs, using the original initial `a0` low 16 bits as an **explicit, externally supplied witness**. Visible outputs are the complete y0,y1,y4,y5 64-bit words; y2,y3 are wholly erased. The circuit introduces no invented condition on the erased words and reconstructs both outputs by independently replaying the exact 64-bit generator after solving. The 16-bit witness is a strong hypothesis, not an observable available for the selected original job.

Source-free [reproducer](../agents/agent3/k04_xoropp_anchored_gap_synthetic.py) imports no H-17 sources, masks, nonce, commitments, or recovered component and uses the system libz3 only. It constructs Boolean carry rules from `a0` and the first observed `y0`, carries a GF(2)-linear state transition across two erased outputs, and imposes the full source-independent 64-bit constraints on observed y1,y4,y5. This is based on the exact output-conditioned Boolean algebra in [Agent5's prior result](h17-k04-outputcondition-64bit-bool-inverse-20261128.md), but supplies the **previously missing positive erasure reconstruction**.

## Independent planted tests

With `a0 & 0xffff` supplied as the correct synthetic anchor, all ten predeclared random full 128-bit planted states (seeds 20261128, 12345, 2027, 2048, 124, 48, 19, 123456, 8773, 2) yielded `SAT` within the five-second-per-instance solver cap; **10/10 initial full states recovered exactly** and the two hidden 64-bit words **both exactly reproduced**. Four deliberately corrupted observed y4 bits (positions 0,17,39,63) with the correct anchor yielded **4/4 UNSAT**. The aggregate local Python invocation completed in 17.37 s, including controls; timings are environment dependent. These 14 tests cover a small planted sample rather than proving that all correctly anchored cases terminate in five seconds.

This is a **conditional complete-output recovery engine**, not an unconditional inversion from the two outer packets. Dropping the anchor leaves the original hard unanchored 64-bit-state problem. A wrong 16-bit anchor gives UNSAT for some original models; its failure cannot reject the entire hypothetical producer family.

## Target-local exploratory discriminator (kept out of public code)

The original intact same-job REQUESTED attempt-1 and REQUESTED attempt-3 packets were used only as hypothesized y0,y1 and y4,y5, respectively; the disputed ACK2 and any physical coupon were withheld completely. Under the same two-word erased-middle/no-reset assumption, anchors were the PS-0417 numeric job suffix parsed in two source-defined ways (literal hexadecimal suffix versus decimal suffix) and the four byte/half-word serializer layouts. **Eight of eight original-source equations returned UNSAT; zero states and zero complete candidate physical coupons followed.**

The job suffix is not authenticated as a producer state anchor, and neither 16-bit parse matches an intact original pair under this particular model. Do not confuse these eight bounded negatives with an exclusion of arbitrary source state, alternative printing algorithms or an authentic physical coupon. No original candidate digest was printed, no PDF or protected source was used, and no original verifier or candidate was edited. The source-dependent test is deliberately not published as public source-bearing CI.

## Next exact recovery condition

The useful remaining step is to identify **an independent, source-warranted 16-bit initial-state observation**, or to eliminate that witness mathematically while preserving planted full-gap recovery. An arbitrary pool of guessed record integers is not evidence of initial producer state. Grouping wrong 16-bit assignments in the current Z3 context did not deliver cheap partial UNSAT cores: the first measured wrong-anchor cores retained all 16 assumptions and dropping one assumption timed out, so a 65,536-cube brute-force is not a practical next step on this implementation.

The known accepted components remain K01,K02,K03,K05,K06,K07; K04 and K08 remain missing and REC8/1 combined acceptance is INCOMPLETE. A valid physical-coupon derivation would still require a producer-to-selected-coupon relation and the unchanged original commitment check.