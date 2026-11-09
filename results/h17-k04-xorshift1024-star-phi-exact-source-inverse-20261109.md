# K04: source-first xorshift1024* and xorshift1024*phi whole-state inverse

**Agent 19 | 9 November 2026 | Conditional emitter exclusion, original six-PASS recovery unchanged**

## Proposed alternate source emitter

Unlike source-matched speculative MT19937 models with 19,937 hidden state bits, both published xorshift1024* generators have only 1,024 state bits and **invertible 64-bit native output multipliers**. If their continuous native output stream formed pairs of whole 64-bit words in printer packets, intact ordinary printer records could recover the entire state independently of the disputed PS-261003-0417 attempt-2 copied ACK. Any successfully source-identified selected stream stage would then yield a complete 16-byte physical coupon.

The two publication-defined output multipliers are:

- S. Vigna's original xorshift1024* M8: `1181783497276652981`. Reference: https://vigna.di.unimi.it/ftp/papers/xorshift.pdf
- xorshift1024*phi: `0x9e3779b97f4a7c13`. Reference: https://svn.apache.org/repos/infra/websites/production/commons/content/proper/commons-rng/commons-rng-docs/jacoco-aggregate/commons-rng-core/org.apache.commons.rng.core.source64/XorShift1024StarPhi.java.html

The common native state transition uses `s0=s[p]`, `p=(p+1)&15`, `s1=s[p]`, `s1^=s1<<31`, `s[p]=s1^s0^(s1>>11)^(s0>>30)` (all words modulo 64 bits). After multiplying each 64-bit observed output by the inverse odd multiplier, the native state transition and each observed full word become an exact GF(2) linear system with 1,024 initial state bits.

## Executed original-source test

Original printer `resources/evidence/print/spool-reconstruction.log`, SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. Training uses the untouched **128 ordinary ACK1 records PS-0300..0427**; excludes all later/selected retries and K04 target commitment. For each multiplier:

- **127** native interpacket output strides 2..128, preserving two consecutive native 64-bit outputs within each packet.
- **Four** original serializers (big/little endian for each 64-bit half, both half orders).
- **508** complete emitter assignments, each tested for native state GF(2) consistency from up to 48 observed outputs.
- **0/508** source-compatible assignments for either multiplier. Every tested assignment contradicts an original whole-word relation during state inversion, before any target test.

Across both variants: **1,016 negative original whole-output models** and **zero recovered K04 coupons**.

## Controls and limits

Each native multiplier and strides 2, 5, and 24 was independently planted with a random 1,024-bit full state. Exact inversion reached **rank 1024**, recovered the entire synthetic original state, and predicted **240 withheld 64-bit native outputs** correctly. Mutation of a training word bit caused a contradiction or incorrect state. Source-first null results are therefore about the generator model, not a failed implementation of linear inversion.

Reproducer: [portable single-file Python SFT](../agents/agent19/k04_xorshift1024_star_source_inverse_sft.py), containing source SHA pinning, six planted tests, full 1,016-case original inversion, and no writes to official artifacts.

This result rejects only the two exact native-64 two-words-per-packet models with their enumerated fixed strides. It does **not** reject truncated halfword emitters, independent per-job seeding, changed stage placement, ciphertext output, or physically modified selected coupons. Historical evidence does not prove either candidate emitter was actually deployed. The larger recovery objective remains K04 + K08 complete accepted values and original combined PASS.

## Same-state-width alternate: xoroshiro1024* / xoroshiro1024** (9 November)

A distinct **published 1,024-bit state transition** (Blackman/Vigna xoroshiro1024, source [Scrambled Linear Pseudorandom Number Generators Fig.2](https://vigna.di.unimi.it/ftp/papers/ScrambledLinear.pdf)) has an equally invertible native output transform, but uses a *different* two-register step: `q=p; s0=s[(p+1)&15]; s15=s[q]; s15 ^= s0; s[q]=rotl(s0,25)^s15^(s15<<27); s[p]=rotl(s15,36)`. The two output variants are `rotl(s0*5,7)*9` (double star) and `s0*0x9e3779b97f4a7c13` (single star), modulo 64 bits.

The exact 1,024-bit GF(2) inverse was implemented separately for this transition, with the original untouched 128 ordinary job packets, the same four whole-native64 endian/half-order serializers and all 127 fixed interpacket strides2..128. Original **508/508** assignments contradict the source for xoroshiro1024*, and **508/508** contradict for xoroshiro1024**; **0** source-consistent emitters and **0** complete K04 coupons.

For each variant, planted full-state inversions at strides2,5,24 recover all 1,024 original state bits (rank1024) and predict **240 synthetic withheld native outputs**; one-bit mutations reject the planted state. See [read-only portable xoroshiro1024 SFT](../agents/agent19/k04_xoroshiro1024_source_inverse_sft.py) (commit `bf3f4dc8eb59381bab723819c81c71c5d6a00099`). The independent locally executed source-equivalent run reported `** positives 3 source_contradicted 508 source_survivors []` and `* positives 3 source_contradicted 508 source_survivors []`.

Combined with the earlier two xorshift1024 multipliers, this is **2,032 source-contradicted whole-native64 producer assignments**, covering four named full-state/scrambler combinations. The scope remains conditional on original packets mapping to two full 64-bit native outputs per record with the enumerated stages; it does not authenticate any physical coupon bit or exclude source-defined truncated/alternate-stage producers. This complete source-only negative is sufficient to stop further work on these four native exact models.
