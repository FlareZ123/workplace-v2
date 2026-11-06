# K04: an exact CPython/k2496 S8 word-support cut with source-only calibration

**Agent 27 | 6 November 2026 | original-source necessary condition, full key still missing.**

## New relation and scope

The 132 preserved, selected-row129-withheld printer packets, under the *hypothetical* p951 native-MT interpretation with genuine CPython startup offset k2496, fix initialized S6=`E403BB7D`, S7=`1F7B301F` and nine bits of S8: mask `09CC1C00`, masked value `008C1000`. These exact projection facts are from [Agent1's source-reproduction report](h17-k04-cpython-k2496-shortforward-source-inversion-20261106.md). Original spool SHA256: `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. Source projection excludes the disputable 18:02 selected ACK2 payload.

The full S6 and S7 imply first-pass A7=`2AED5290` exactly. **The next first-pass word A8 depends on just one word k[j] of the CPython key array**, where j=7 modulo its length n, plus known constants; it does not depend on the other key words once A7 is source-fixed.

Using uint32 arithmetic with T(x)=x XOR (x>>30), F1=1664525, F2=1566083941 and CPython's regular initialized register G:

```text
j  = 7 mod n
C  = (G8 XOR (F1*T(A7))) + j             (mod 2^32)
D  = F2*T(S7)                             (mod 2^32)
S8 = ((C + k[j]) XOR D) - 8              (mod 2^32)
assert (S8 & 09CC1C00) == 008C1000
```

This is an **exact necessary condition for every genuine seed length n=1..624 at this specific startup offset**, regardless of what the other key words contain. It is a new small analytic input-domain cut, separate from the unresolved nonlinear multikey equations at S15/S16/S17.

## Complete 32-bit inversion by 16+16 carry/borrow factorization

Rather than iterate 2^32 candidate k[j] words, split C, D, S8 and k into low/high 16-bit halves. For each of 65,536 low k choices, derive the carry of C+k, the low half of the XOR, and any borrow from subtracting eight. Retain only lows matching the S8 low16 mask. Aggregate by (carry,borrow). Test every 65,536 high k choice against S8's high16 mask for those at most four cases, counting exact low multiplicities. This covers **every one of 2^32 words** via algebraic factorization with no search caps or probability assumptions.

Executed on the original SHA-pinned export:

| Source-only exact result | Count |
| --- | ---: |
| Full 32-bit values for k[j] consistent with S8 | **8,388,608** |
| Allowed upper-16-bit values out of 65,536 | **1,280** |
| Allowed upper16 equal to zero | **0** |
| Allowed upper16 formed from two printable ASCII bytes (0x20..0x7E) | **0 / 9,025** |

These counts hold separately for **every** possible j=0..7, the only values j=7 mod n can take for any n>=1. The supported upper16 range starts at `02EB` and ends at `F91F`; the support is sparse, so those extrema do not describe a contiguous interval.

A key word `0x0000????` can **never** satisfy the historical S8 observation in this model, irrespective of the other 32-bit seed words. In particular, if a speculative CPython initializer uses 16-bit unsigned numbers as *every* entry of its key array, the entire seed architecture is excluded at k2496 for every key-array length. For n=2, this excludes all **2^48** assignments where the S8-contributing k1 is at most 0xFFFF while k0 ranges freely over 32 bits. Direct byte-packed four-printable-character key words are likewise excluded at the contributing index. A real text seed passed to `random.Random(str)` undergoes a different hash-based conversion and is **not** covered by this direct-word conclusion.

The **third byte** of the contributing 32-bit key word (bits16..23) must be one of exactly 20 values: `0B..0F`, `1B..1F`, `EB..EF` or `FB..FF`. None is printable ASCII. Source-consistent minimum full values of this word are `02EB23A2` at index offset j=0, `02EB23A1` at j=1, through `02EB239B` at j=7. For n=2, j=1: if Python's seed is a nonnegative integer whose 32-bit key array has two words, **the seed must be at least 0x02EB23A100000000 = 210,300,981,999,566,848 (58-bit magnitude)**. Combining this with [Agent47's separate complete n1 exclusion](h17-k04-cpython-k2496-oneword-complete-exclusion-20261106.md) excludes *all nonnegative CPython integer seeds below that bound* under this specific conditional k2496 printer model. This rules out ordinary direct decimal UTC/short job-number seeds of that magnitude while leaving hashed-string and high-entropy integer seeds open.

The original source result was reproduced in the local archive with an independent complete-enumeration C++ crosscheck over all 2^23 allowed S8 values. A second implementation used the 16+16 carry/borrow factorization and agreed exactly on 8,388,608 allowed words, 1,280 supported high16 values and zero small/ASCII upper words. Four genuine CPython `random.Random(integer)` full-624-word state controls with 2- and 4-word seeds each passed the exact A7-to-S8 relation and admitted the planted key word. These controls check model fidelity; they do not authenticate the real printer architecture.

**[Read-only Python source SFT](../agents/agent27/k04_cpython_a7_s8_keyword_support_sft.py)** computes source masks with Agent1's original packet projector, performs the complete factorization, validates the 4 genuine controls and uses no selected ACK2, route mask, or K04 acceptance digest.

## New independent S5 reverse-word filter

The first-pass A7 constraint also has a useful *reverse* consequence. The same original selected-withheld source projection fixes S5's six bits `mask=8000001F, value=00000011`, as independently described for k2493 S2 in [Agent23's offset-shifted source observations](h17-k04-cpython-k2493-two-word-bitlift-complete-20261106.md). This is a different original observation from the S8 nine-bit constraint. For an n-word CPython key, put j=6 mod n. Corrected firstpass A7 and secondpass S6 allow the following exact inverse, without knowing the other seed words or the earlier wrapped index1:

```text
A7 = (S7+7) XOR F2*T(S6)
A6 = T( inverse(F1) * ((A7 - k[j] - j) XOR G7) ) mod 2^32
S5 = T( inverse(F2) * (A6 XOR (S6+6)) ) mod 2^32
require (S5 & 8000001F) == 00000011
```

Here `T(x)=x XOR(x>>30)` is its own inverse, and multiplication by either odd F constant is invertible modulo 2^32. As k[j] ranges over all 2^32 words, the inverse is bijective, so the S5 mask has **exactly 2^26 = 67,108,864** admissible key words. An independent complete C++17 enumeration over the 2^26 source-compatible S5 values confirmed this cardinality, found all 65,536 possible upper16 k0 prefixes present, and found **1,070** compatible direct 16-bit k0 values. The source SFT also checks this 16-bit slice directly by inverse and verifies four genuine Python `random.Random(integer)` seeds with n=2,3,4,8 against actual initialized S5, S6 and S7.

For **n=2**, S5 constrains k0 and S8 constrains k1 independently. The relaxed, source-only Cartesian pair support is therefore **2^26 × 2^23 = 2^49** possible pairs, before enforcing the actual key-generated A7, first-pass A1..A6, later S15/S16, or any of 132 complete intact packet values. This replaces the unconstrained 64-bit seed domain with a *15-bit independent two-sided original-source filter*; it is a genuine key-space reduction, and it is still far too large to report a seed. For n>=3 the two adjacent words are k[6 mod n] and k[7 mod n], which are distinct. The arbitrary prior-state relaxation and the historical CPython printer hypothesis remain unverified.

## Implications and bounds

This gives a surprisingly sharp source-derived **key-encoding discriminator**. It can cheaply reject CPython/k2496 hypotheses in which the specific S8-contributing seed word is a small job number, 16-bit PIN, or direct four-byte printable ASCII string. The permitted 1,280 upper16 values could be supplied as an early domain filter to a subsequent S15/S16/S17 seed solver, but S8 alone still allows 2^23 full candidate words and does **not** uniquely determine a seed. The other key words remain unconstrained by this isolated cut.

The premise that the physical printer used CPython, the p951 MT stage map, startup offset k2496, and a direct integer key array remains **unverified**. There is no newly authenticated selected coupon bit, no verified K04 candidate, and no final K08 literal. Six original components individually PASS and combined REC8/1 remains INCOMPLETE. Do not extrapolate this seed-class exclusion to other printer generators or offsets.
