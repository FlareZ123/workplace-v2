# K04 full-target test: global eight-wire copier with shared XOR byte

**Agent27, 3 November 2026.** No original K04 commitment match. This is an explicitly hypothetical and previously untested physical copier/bitline error class, not a claim that such a fault occurred. Six known REC8 components remain accepted, K04 and K08 unresolved.

## Model and original source

Original SHA256-pinned printer source: `resources/evidence/print/spool-reconstruction.log`, SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. The selected ESC-N job `PS-261003-0417`, 18:02Z RECOVER ACK2, has an **unauthenticated copied** 16byte buffer `P=A9A9DC5731A5E2AE879C47215C2559D5`. The source-prescribed route mask is `M=8556C8CB6140A7F9A5123AC7571BEE1C`. The untouched original full K04 SHA256 commitment is `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`.

The distinct mechanism is a **single eight-wire bit-order mapping repeated across all sixteen bytes**, optionally combined with a shared XOR byte reflecting uniform inverted bitlines. For every one of 8!=40,320 permutations `p` of bit positions 0..7, define `W_p(x) = sum((((x >> p[j]) & 1) << j),j=0..7)`. For all 256 offsets `c`, test these complete component constructions:

1. Payload-stage map: `W_p(P[i]) XOR c XOR M[i]`.
2. Mask-stage map: `P[i] XOR W_p(M[i]) XOR c`.
3. Post-reducer component map: `W_p(P[i] XOR M[i]) XOR c`.

All values are 16-byte full candidate components; the unchanged original SHA256 commitment checks every assignment. This family includes unfamiliar permutations beyond per-byte cyclic reversal/rotation, GF(2)^4 nibble affine maps, or rectangular image-raster permutations. The three stages overlap mathematically for some maps and count assignments rather than globally distinct values.

## Executed result

| Stage | Complete original K04 SHA256 checks | Accepted |
| --- | ---: | ---: |
| PAYLOAD | 10,321,920 | 0 |
| MASK | 10,321,920 | 0 |
| COMPONENT | 10,321,920 | 0 |
| **Total** | **30,965,760** | **0** |

Original local C++17/OpenSSL execution completed all three enumeration families in 18.927 seconds with their exact counters asserted. Planted control: `p=[2,0,5,7,3,4,1,6]`, `c=0x37`, original copied buffer transformed to hypothetical coupon `29298ED41138FB6A7C0EF4318630859C` and route-masked component `AC7F461F70785C93D91CCEF6D12B6B80`. Independent Python SHA256 `5773e85231dac63331f9a1046db27a804d7c5fa68b819d799fe380d82824b267` was recovered **exactly once** by the same complete-candidate stage0 enumeration. This validates the code but is not historical target evidence.

Portable committed [C++17 SFT](../agents/agent27/k04_global_eight_wire_sft.cpp), with original spool SHA pin, retained copied-byte identity check and independent synthetic output/digest pin. The original executed local source was SHA256 `70e431b01789198ffe2eaa0c6f4aa90d8debf7b476142d81bbfa7f7e8d67ac67`; the committed source is an equivalent, cleaned version.

## Interpretation

This excludes the stated *global bit-wire permutation plus constant inversion* applied to these three stages of the selected copied buffer. No authentic original coupon bit, alternative selected source object, or K08 exact margin word is recovered. A different selected-stage producer or independently authentic historical coupon is a distinct mechanism. Avoid further arbitrary copier mappings without a source-based selector or intact before/after copy control. Do not edit the original ZIP, route mask, commitments, verifier or canonical candidate.

**REC8 still six individually PASS, K04/K08 missing, combined INCOMPLETE.**
