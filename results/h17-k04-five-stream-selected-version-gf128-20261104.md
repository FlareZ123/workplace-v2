# K04: five original selected streams as a GF128 version-postprocessor discriminator

**Agent 3, 4 November 2026 | source-pinned test | K04 and K08 remain missing.**

## New constructive mechanism

The original archive retains **five complete 16-byte older-versus-selected record pairs** from different domains. A hypothetical universal selected-version operator could map an earlier original object to its accepted replacement. Fit a whole-packet transformation on genuine pairs and require it to reproduce independent, withheld selected objects. If supported, predict a complete ESC-N coupon from another retained same-job packet, XOR the original route mask, and SHA256-check the unchanged K04 commitment.

There is no original publisher specification attesting a shared postprocessor. These are genuine version/selection relationships, although revision transitions in different record types may have no common construction.

| Source | Earlier original 16-byte block | Selected original 16-byte block |
|---|---|---|
| K02, GOOD LT204 lower→higher DIAG_WORD revisions | BB1E82F3BFB3479E5358255316967CAA | E1A5E474BAD7E853A2E8C71D3317D507 |
| K03, PTW417 earlier→highest signed CLOSED AS_LEFT suffixes | AD1D814B64B2EE4A574A92325CB72EE5 | D7DAD6BC9714519B7DAD0AD4BE8E87FD |
| K05, TRP2 seq200→seq300 CONTROL quartet | 42BFD0538052760C6FC2B743BFB00270 | FF8B78200A56E8586DCDA00EF01E4572 |
| K06, RC17 withdrawn B→issued C service strips | D82A73E9E1DB4379759E0027C130C9BB | 5DBF40EE52FAAED9A536D3326CF0D95A |
| K07, AX7778 drill→AX7782 committed checkpoints | AC5FBCDD1CB5C98CA234AE35DD42B16A | 8947CEDCB9CC73BAB7E87BE63302C5C9 |

The K03 signed A-bay revision1 has a second retained serial suffix, 7E73B4CC, in place of 574A9232. Both authentic alternatives are independently tested. The selected K02 and K07 prehash blocks reproduce their known accepted SHA256-first16 values; K05 and K06 selected blocks are themselves known accepted components.

## Recoverable operator and holdouts

In GF(2^128) with polynomial x^128+x^7+x^2+x+1, two distinct pairs uniquely define an **affine** operator T(x)=Ax+B; three define a **quadratic** operator T(x)=Ax²+Bx+C. For each field-value layout, test all 10 two-pair or 10 three-pair training subsets. Eight invertible views cover reversal of four 32-bit words, reversal of bytes in each word, and bit reversal in bytes.

The quadratic solve uses characteristic-two identities: U=(y1+y2)/(x1+x2), V=(y1+y3)/(x1+x3), A=(U+V)/(x2+x3), B=U+A(x1+x2), C=y1+Ax1²+Bx1. Here + means XOR. A planted genuine quadratic publisher with five original-shaped records passes **all 10 distinct training-triple constructions and all heldout 16-byte predictions**.

The exact test gave:

| Diagnostic | Original result |
|---|---:|
| Source-supported independent old/new pairs | 5, plus K03 old A-rev1 alternative |
| Source-fitted affine models | 160 |
| Source-fitted quadratic models | 160 |
| Full 16-byte historical heldout selected-record matches | **0** |
| Complete K04 coupon-derived component checks | **960** |
| Authentic K04 SHA256 commitment matches | **0** |
| Synthetic five-record quadratic publisher training and holdouts | **PASS** |

Each 320 fitted operator also predicted a coupon from three original prior same-job objects, excluding the disputed selected 18:02 ACK2 buffer: 18:01 RECOVER request1, 18:03 RECOVER request3, and 16:45 LABEL ACK. Predictions underwent the original XOR route mask and full unchanged K04 SHA256 acceptance check.

**Conclusion:** These finite, exact universal affine/quadratic historical version-postprocessor models lack any full independent source-pair support, and none reaches the K04 target. Higher-degree polynomial interpolation can fit almost any small dataset and would be underconstrained here. An authenticated printer-generation/capture bridge or author-final K08 text witness remains more valuable than raising polynomial degree. This is neither a recovered physical coupon nor a proof of general impossibility.

Source SHA256 pins, five original pair vectors, synthetic positives and reproducible target tests are preserved in [Agent 3's standalone SFT](../agents/agent3/k04_selected_gf128_postprocessor_sft.py). No archival source, mask, acceptance, verifier or canonical candidate changed.
