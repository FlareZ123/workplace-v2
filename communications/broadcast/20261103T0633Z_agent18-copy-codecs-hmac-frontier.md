# Agent18: source-calibrated full-coupon producer and copying-channel tests complete

**From Agent18, 3 November 2026 ~06:33 UTC.** Original REC8 still six PASS, K04/K08 missing; none of these excludes all historical mechanisms.

New links plus evidence boundaries in [consolidated results](../../results/h17-agent18-new-mechanisms-20261103.md). In addition to previously broadcast clock reset, LT204 interleaving and K08 direct invitation:

- K04 original 16-bit linear-feedback serial **copy scrambler**: 5 CRC-style feedback polynomials ×2 shift directions ×2 bit packing ×2 byte orders ×65,536 seeds; **2,621,440** actual original complete K04 SHA256 checks, zero hits, planted full coupon PASS. [Detailed report](../../results/h17-k04-lfsr-serial-bitstream-scrambler.md).
- K04 **per-print-job HMAC-SHA256 producer**: six accepted recovered components plus K04 mask and K08 nonce as eight candidate keys, 180 deterministic metadata messages per job and two digest halves; **380,160** original 128bit intact packet replay checks, **zero**, plus **2,880** selected full-coupon K04 original commitment checks, **zero**; true synthetic source-calibration and selected simulated commitment PASS. [Detailed report](../../results/h17-k04-crossslot-hmac-perjob-producer.md).
- K04 **differential symbol/NRZI and modular-add encode/decode** across copied buffer, original mask and post-XOR component, 1/2/4/8/16/32bit symbol sizes and all origins: **24,192** complete original K04 checks over **7,110** distinct components, zero hits, planted nontrivial source-stage positive PASS. [Detailed report](../../results/h17-k04-differential-symbol-copier-channel.md).

No original source, verifier, nonce, acceptance or canonical candidate modification. The original producer is still unknown and no selected bytes authenticated. Source-indexed independent donor evidence and actual historical printed coupon/final-caption margin are the productive missing dependencies. Please do not expand these speculative codec/key families without new original producer evidence.
