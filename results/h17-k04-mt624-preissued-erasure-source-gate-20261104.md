# K04: 624-word native-MT erasure recovery using cross-archive source controls

**Agent 25 | 4 November 2026 | complete unknown-coupon reconstruction mechanism, source-calibrated negative.** This is an experimentally tested alternative to the prior p951 hidden-stage inversion: place an entire withheld 16-byte packet *before* the 128 ordinary print packets, then invert an MT19937 twist using exact native words supplied by different original record types. **No historical K04 commitment match, physically authenticated coupon bit, or K08 caption is recovered.** Six original components remain accepted and combined REC8 incomplete.

## Distinct target-reaching hypothesis

MT19937's native 32-bit output recurrence is

```
X[t+624] = X[t+397] XOR (((X[t] & 0x80000000)
             | (X[t+1] & 0x7FFFFFFF)) >> 1)
             XOR (0x9908B0DF if X[t+1] & 1 else 0).
```

Undo standard MT tempering for every original source word. Hypothesize a single contiguous MT stream with four known precursor words `X[0..3]`, four completely erased coupon words `X[4..7]`, and **624 subsequently observed words `X[8..631]`**. Apply the eight recurrence equations for t=7 down to0. Each equation reveals the top bit of X[t] and lower31 bits of X[t+1]. Together these reconstruct **all 128 bits of the erased coupon** and simultaneously enforce exact source consistency. The reconstruction uses neither a physical copy of the selected ACK nor commitment feedback. Four genuine seeded Python MT19937 source streams (seeds 1,42,5489,0x89ABCDEF) each recovered an independently hidden full coupon exactly.

**Critical historical uncertainty:** the original source does not say that the printer, recorder and signed recovery fields shared one native MT19937 stream, or that their records were emitted contiguously in the proposed order. This is a candidate-generation architecture, not an authenticated history.

## Original-source holdout and K04 gate

The original printer spool SHA256 is `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. The selected 18:02 copied ACK is **excluded throughout**. Candidate precursor groups: actual K01 signed ink, K02 selected telemetry prehash, K06 approved-page strips, K07 selected checkpoint prehash, recorded K04 mask, and K08 desk nonce. Actual after-stream groups: 128 complete unselected ordinary spool packets, original recorder controls and independently preserved late printer packet bodies.

For a source-level whole-coupon holdout, hide the intact **07:00 ordinary printer packet** and construct 624 supposed future native words from the other127 ordinary printer packets (508 words), 88 recorder control words, five alternative precursor groups (20 words), and two distinct late printer packets (8 words). Test every precursor (6), all source/printer/late 32-bit endian assignments (8), and all ordered two-late-packet choices (12). **All 576 complete original-source histories are MT-recurrence-inconsistent**; zero predicts the original 16-byte held-out packet.

For the actual K04 physical coupon hypothesis, use the 128 intact ordinary packets (512 words), the 88 recorder controls, five non-precursor 16-byte groups (20 words), and one of four intact late packets (4 words). Six precursor selections × eight byte-order assignments × four late-packet choices = **192** hypotheses. **Zero** satisfies the necessary native recurrence; no original-K04 SHA256 hit results. This excludes this precisely specified contiguous cross-source ordering only. The route mask and original K04 commitment remain unchanged.

## New strict four-byte native-tail signature

Under the proposed stream geometry, recurrence t=7 predicts the final native X[631] word from preserved ordinary printer native X[8] and X[404], up to one unknown high bit of X[7]. Considering both raw printer word endiannesses and both resulting output endiannesses yields exactly eight necessary terminal byte tokens:

`18B889FE, 294BE3B0, 2B5AEBF4, 5CB098FC, B0E34B29, F4EB5A2B, FC98B05C, FE89B818`.

A literal substring scan of the original unpacked local archive file bytes returned **zero matches** for these tokens. This is an independently checkable necessary-condition negative for a source-copy that preserved the native terminal output word verbatim, not proof no differently encoded or unseen future native donor exists.

## Reproducibility and interpretation

[Original-source read-only single-file SFT](../agents/agent25/k04_mt624_preissue_crosssource_sft.py) implements temper inversion, inverse recurrence, four seeded complete-coupon positive controls, 576 intact-source holdouts, 192 original-target hypotheses and exact original 4-byte token search. It relies on Python 3 standard library, the immutable original `resources/`, and no CI workflow. The locally executed source-equivalent variant printed **576/0, 192/0, four seeded positives**; the committed full-source variant retains the exact model, cardinalities and assertions. No selected original K04 coupon, Emily final K08 text, original evidence, verifier, acceptance commitment or canonical candidate was modified.

**Result:** an alternative *full 128-bit* MT coupon erasure reconstruction is mathematically possible from one precursor quartet and 624 authentic future native words, but the tested archival cross-source joins do **not** meet those conditions. Subsequent investigations should use a **historically evidenced producer stage or high-coverage source carrier**, rather than treating these artificial joins as actual copies of the lost selected coupon.
