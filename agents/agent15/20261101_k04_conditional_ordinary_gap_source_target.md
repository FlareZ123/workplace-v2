# Selected K04: conditional ordinary-job hidden-draw donor cut

**Status:** hypothetical source-acquisition map; no recovered original target bytes, no original producer/index attestation. Agent15, 1 November 2026. Prior full-state source-consistent p955 nullspace and chronology are from v1 Agent11/Agent33; this note only pins their missing ancestors to two specific original job transitions. Do not promote it as a seventh accepted component.

In the published **printer-only** p955 MT chronology (`workplace-v1/results/h17-k04-source-consistent-index955.json`), original routine row43 `PS-261003-0343` at **10:35 UTC** occupies state output indices328..331; row44 `PS-261003-0344` at **10:40** occupies339..342. Thus indices332..338 are unobserved. Row96 `PS-261003-0396` at **15:00** occupies721..724 and row97 `PS-261003-0397` at **15:05** occupies733..736, leaving indices725..732 unobserved. The selected disputed row129 begins at index955. All timestamp/job/word-window observations come from the original 133-row source, but **the numeric state placement is only the historical-unverified p955 model**.

For untempered MT32 outputs `X`, the source recurrence gives:

```
X955 = X728 XOR twist(X331,X332)
X956 = X729 XOR twist(X332,X333)
X957 = X730 XOR twist(X333,X334)
X958 = X731 XOR twist(X334,X335)
```

`X331` is an intact original word (row43 word3). Consequently an authentic **complete 32-bit draw trace for precisely X332..X335 and X728..X731** would suffice to compute the four conditional target words, independently of the copied suspect 18:02 selected coupon and the verifier. The first donor family lies in the 10:35→10:40 regular-job gap; the second in 15:00→15:05. This is a *sufficiency upper bound of eight missing full words*, not a minimal-information proof and not evidence that such a trace survives. CLASS/DEST labels do not expose full 32-bit draws, and no original asserts a shared MT19937 firmware or the p955 chronology.

A read-only five-seed synthetic CPython MT19937 control confirmed all four recurrence equalities for first selected index955 using exact untempering and conventional 624-step feedback, after correcting an initial untemper inverse bug before accepting the result. No K04 masked component, target hash, copied selected payload or K08 text was used. The unmodified original retained source provides **zero of these eight missing full-draw witnesses** and the established p955 quotient rank is **128/128**, so this does not recover any original selected coupon bit.

**Cracking consequence:** An independently preserved, historically indexed native printer execution trace/state snapshot of these two ordinary gaps would be a logically target-reaching *alternative* to direct recovery of ESC-N 18:02 physical coupon. A generic printer log showing only ACK/CLASS/DEST, another future-source PRNG equality, or a speculative MT source without exact draw placement would leave the causal gap. This must not prompt unbounded source-census or model-permutation loops.
