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

The original source result was reproduced in the local archive with an independent complete-enumeration C++ crosscheck over all 2^23 allowed S8 values. A second implementation used the 16+16 carry/borrow factorization and agreed exactly on 8,388,608 allowed words, 1,280 supported high16 values and zero small/ASCII upper words. Four genuine CPython `random.Random(integer)` full-624-word state controls with 2- and 4-word seeds each passed the exact A7-to-S8 relation and admitted the planted key word. These controls check model fidelity; they do not authenticate the real printer architecture.

**[Read-only Python source SFT](../agents/agent27/k04_cpython_a7_s8_keyword_support_sft.py)** computes source masks with Agent1's original packet projector, performs the complete factorization, validates the 4 genuine controls and uses no selected ACK2, route mask, or K04 acceptance digest.

## Implications and bounds

This gives a surprisingly sharp source-derived **key-encoding discriminator**. It can cheaply reject CPython/k2496 hypotheses in which the specific S8-contributing seed word is a small job number, 16-bit PIN, or direct four-byte printable ASCII string. The permitted 1,280 upper16 values could be supplied as an early domain filter to a subsequent S15/S16/S17 seed solver, but S8 alone still allows 2^23 full candidate words and does **not** uniquely determine a seed. The other key words remain unconstrained by this isolated cut.

The premise that the physical printer used CPython, the p951 MT stage map, startup offset k2496, and a direct integer key array remains **unverified**. There is no newly authenticated selected coupon bit, no verified K04 candidate, and no final K08 literal. Six original components individually PASS and combined REC8/1 remains INCOMPLETE. Do not extrapolate this seed-class exclusion to other printer generators or offsets.
