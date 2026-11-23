# K04: exact two-output xorshift128+ inversions and 12,254,869 whole-coupon gap checks

**Agent 7 | 23 November 2026 | Original K04 SHA256 commitment matches: ZERO.** K04 and K08 remain MISSING; six earlier components remain individually accepted, REC8/1 INCOMPLETE.

## Complete-output mathematical reconstruction

The original PS-261003-0417 RECOVER records include two independently retained 16-byte REQUESTED packets: 18:01Z attempt1 and 18:03Z attempt3. The copied 18:02Z ACK attempt2 is excluded entirely. This experiment asks whether the physical middle coupon consists of two adjacent 64-bit modulo-sum outputs from a shared xorshift128+ generator. That generator assumption has no historical confirmation.

Two complete two-output inversions can be performed by bounded native exhaustive lifting, avoiding the solver liveness problems of related 128-bit generator searches:

1. **V8 transition (23,17,26).** From first output x0, write state after x0 as (L1,R1) and L1=x0-R1 modulo 2^64. The second output x1 yields next state word R2=x1-R1. The XOR recurrence determines 38 upper bits of R1 from a guessed 26-bit lower prefix. Exhaust 2^26 prefixes. This implements an independently written version of the published [Scott Contini bit-lift inversion](https://github.com/ScottContini/a_better_xorshift128-inverter), MIT license.
2. **Vigna transition (23,18,5).** The recurrence has bit identity R2[i] = L1[i] xor L1[i-23] xor L1[i+18] xor L1[i-5] xor R1[i] xor R1[i+5], treating out-of-range terms as zero. Given the low 18 bits of R1, ascending i=0..45 determines the remaining 46 bits exactly, including subtraction borrows. Exhaust 2^18 prefixes. The generator variant is documented in [Vigna's xorshift+ paper](https://vigna.di.unimi.it/ftp/papers/xorshiftplus.pdf).

For each original source packet, independently test **48** whole 16-byte serializers: all 24 permutations of its four 32-bit chunks, globally big- or little-endian. Decode the two candidate 64-bit outputs. Fit **every** exact first-pair source state with no symbolic solver timeout or model cap. REQUESTED1 predicts whole coupon pairs forward; REQUESTED3 predicts whole coupon pairs backward with the exact inverse state transition.

Every 16-byte predicted coupon is XORed with the original K04 route mask, then compared using the full SHA256 of the 16-byte component and the unchanged original commitment. The immediate-gap central coupon is tested first. The replay additionally scans **65,533 contiguous whole two-output windows forward**, or **65,535 backward**, per fitted source state, allowing unknown intervening native draws. The full opposite REQUESTED packet is a separate 128-bit holdout.

## Completed original-source measurements

Read-only source printer SHA256: 7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083.

Original route XOR mask: 8556C8CB6140A7F9A5123AC7571BEE1C.

Original K04 component SHA256 commitment: 930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0.

| Generator | Source views (48 layouts × 2 anchors) | REQUESTED1 full-state fits | REQUESTED3 full-state fits | Complete original K04 SHA256 assignments | K04 hits |
| --- | ---: | ---: | ---: | ---: | ---: |
| V8 xorshift128+ (23,17,26) | 96 | 47 | 42 | **5,832,521** | **0** |
| Vigna xorshift128+ (23,18,5) | 96 | 41 | 57 | **6,422,348** | **0** |
| **Combined** | **192** | **88** | **99** | **12,254,869** | **0** |

All 187 full source states were enumerated with original data, and all **187 immediately adjacent full coupons** failed the original target before the longer window scan. **Zero** states reproduced the opposite complete REQUESTED packet in the same serialization. The broader 65k scans also yielded zero original target hits. No genuine missing coupon bit was recovered.

Original special RECOVER source bytes: REQUESTED1 CD3E4F216ADB2FB180DA2AA90B33F7A4; REQUESTED3 44D53DFC29D7943A95D89371DA58EC64. The unrelated 16:45Z routine PS-261003-0417 ACK packet was excluded from RECOVER-stage fitting through its timestamp/class. The 18:02Z selected ACK payload was not a fitted model input.

## Planted whole-object and inversion controls

V8 inverse: five independently generated exact 128-bit state plus four future-output recoveries PASS. Vigna inverse: eight such recoveries PASS. Both transition inverses passed 100,000 seeded complete-state round trips.

The original-mask whole-SHA256 native scanner successfully detected synthetic full 16-byte planted coupons at window indices **2, 42 and 1,234**, in **both forward and backward directions and for both generator variants**. The planting also exercised a nontrivial 32-bit permutation (2,0,3,1) with little-endian chunks, giving twelve independent planted full-target scans. Synthetic checks never substitute for original acceptance.

## Reproducible source-pinned code

The [complete single-file SFT orchestrator](../agents/agent7/k04_xs128p_complete_windows_sft.py) compiles:

- [V8 exact 26-bit inverter](../agents/agent7/k04_xs128p_inverse.c).
- [Vigna exact 18-bit inverter](../agents/agent7/k04_xs128p_vigna235_inverse.c).
- [Two-variant full 65k-gap SHA256 scanner](../agents/agent7/k04_xs128p_dual_gap_scan.c).

Focused original-source and planted controls also remain in the [V8 forward SFT](../agents/agent7/k04_xs128p_source_sft.py) and [backward SFT](../agents/agent7/k04_xs128p_reverse_source_sft.py). The main SFT uses unchanged resources by default, or the optional uploaded original ZIP, and requires a C compiler plus OpenSSL/libcrypto.

## Meaning and further work

The original complete-output negative **excludes exactly** these two 128-bit state transitions, 48 physical serializers, both retained REQUESTED anchors and first 65k consecutive two-output selected-coupon windows. It cannot exclude a different producer, independently seeded attempts, other packet encodings, a copied-ACK fault, a later physical coupon, or the still-unknown K08 author-final wording. The exact finite inversion is a reusable research tool, but increasing the same model's gap or source endian variants has low justification without a new source clue.

Original verifier remains **6/8 PASS; K04 and K08 MISSING; combined INCOMPLETE**.
