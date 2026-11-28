# K04 — exact cyclic CRC16 recovery from AX-7782 checkpoint sequences

**Agent 3 · 28 November 2026 · original K04 commitment NO_MATCH.** The six historically accepted slots remain PASS; K04 and K08 remain MISSING, with combined REC8/1 INCOMPLETE. This is an original-source **conditional** producer test, not an authenticated link between the transfer ledger and the physical printer coupon.

## Distinct mechanism and exact 128-bit inverse

Suppose an eight-position AX-7782 checkpoint sequence represents a single 16-byte physical coupon P, with checkpoint i equal to a CRC16 of P circularly rotated by 2i bytes. The surviving transfer ledger contains two-byte checkpoints at eight selected positions. Unlike earlier one-halfword CRC mappings or **cumulative CRC-chain** proposals, this model assigns each checkpoint to a whole 16-byte rotated coupon. It can therefore constrain all 128 coupon bits at once.

Write the unknown two-byte coupon words as B0,...,B7, and let D_i denote the zero-initialized CRC remainder of B_i for an arbitrary degree-16 generator p(x). Let L advance any 16-bit register by two zero bytes. For the eight CRCs C_i of the rotated full coupon, linearity gives

```
C_(i+1) XOR L(C_i) = (I XOR L^8) D_i      (indices modulo 8).
D_i = inverse(I XOR L^8) (C_(i+1) XOR L(C_i)).
B_i = inverse(x^16 mod p) D_i.
```

The 16-byte coupon is the concatenation of the eight recovered B_i. A fixed CRC init/xorout adds the same affine constant to every C_i, which can be subtracted before applying the inverse.

**Exact invertibility classification:** For all polynomials with constant term one and p(1)=1, x^128+1=(x+1)^128 is coprime to p, so `I XOR L^8` is invertible and the mapping has **full 128/128 GF(2) rank**. No guesswork or SAT is needed for a fixed polynomial/checkpoint representation. For a polynomial with p(1)=0, the CRC of a circular byte rotation preserves a parity constraint; original transfer checkpoint positions have mutually incompatible parity even when either retained retry value can be selected for each position. Thus the entire x+1-divisible polynomial subfamily fails this model's source-only consistency requirement. This classification is about the cyclic-CRC hypothesis, not all possible encoders.

## Full original-source outcome

Two executed source-pinned experiments used only the existing local historical transfer ledger, route mask and unchanged K04 SHA256 commitment. Both applied the source-selected AX-7782 sequence. No PDF or protected material was accessed, no public original-bearing CI ran, and no original records, verifier, acceptance file or candidate were modified.

**All invertible CRC16 generators.** Exhausted all 16,384 monic degree-16 generator polynomials with constant term one and p(1)=1. Each generated two checkpoint byte orientations, two cyclic index directions, two init states, two xorouts, eight coupon word-rotation offsets and two complete-output reversals. A total of **4,194,304** complete source-dependent component assignments were formed; within each of the two 8,192-polynomial disjoint shards, exact complete original SHA256 checks were 2,097,024 and 2,097,152 respectively (the first shard had 128 duplicate coupon strings). **Zero original K04 commitment matches.** Twenty-four independently generated full-length synthetic CRC/initialization controls recovered their exact planted coupons.

**Unknown CRC register / copied ACK bridge.** To avoid treating init/xorout as known, a separate reduction observes that a free affine checkpoint salt changes all recovered two-byte coupon words by the **same unknown two-byte XOR pad**. Under the hypothesis that at least one two-byte word of the unverified copied selected ACK survived unchanged, that pad is one of the eight pairwise differences between the reconstructed coupon and copied ACK. An additional bitwise-majority pad was tested as a separate noisy-copy proposal. Exhaustively combined the same 16,384 polynomials with 4 independent bit-reflection modes, 2 checkpoint byte orientations, 2 sequence directions, 8 rotations, whole-coupon reversal and within-word swap: **8,388,608 source-model layouts**. After collapsing duplicate pad guesses within a layout, **75,444,805 complete original K04 commitment comparisons**, **zero matches**. Five independent planted full-coupon controls, including recovery of a common pad despite four corrupted copied bits, passed. The best residual against the copied ACK across all layouts was 26 bits; a fixed independent pseudo-random comparator had a minimum of 27 bits. That proximity does **not** authenticate a transfer-to-coupon link.

The exhaustive tests do not cover nonlinear transfer encoders, noncyclic windows, an entirely independent printer value, unconstrained checkpoint mixing, or a copied buffer with *every* two-byte position damaged in an arbitrary way. They do rule out this entire invertible cyclic-CRC polynomial family under the frozen layouts and the stated finite copy-bridge hypothesis, not merely common named CRCs.

## Why it matters and next decision

The construction reveals a previously untested **one-to-one, full 128-bit recovery mechanism** from the eight source-selected two-byte checkpoints; its algebraic proof and planted controls hold independently of H-17. The actual source/commitment negative now sharply rejects this particular transfer-code explanation. Do not rerun CRC polynomial/init/name variants or enlarge unguided copied-ACK correction searches on the strength of this failed coupling.

The missing decisive relation remains which original producer (if any) jointly generated the transfer checkpoint sequence and a selected physical printer coupon. K08 remains a separate unsolved **complete author-final wording** problem; this experiment emits no K08 text.

Reproducers: [pure-Python all-polynomial inverse](../agents/agent3/k04_crc16_cyclic_fullcoupon_solver.py) and [C++ unknown-init/copy bridge](../agents/agent3/k04_crc16_copy_bridge_sft.cpp). Both are meant for local, read-only original-resource execution with aggregate-only stdout; neither is a public original-data workflow.
