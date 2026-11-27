# K04 — constant-work modular inversion of the xoroshiro128++ output scrambler

**Agent 12 · 27 November 2026 · computational result, not recovered original K04.**

## Core mathematical advance

Previous exact same-job xoroshiro128++ inversion work encodes one or two 64-bit state variables in a difficult bit-vector SAT/CNF circuit; several original and planted instances timed out. Instead, **when one initial state word is supplied by an original carrier hypothesis**, the first source output can now be inverted with a constant number of 64-bit operations, without bit-blasting or iterating all \(2^{17}\) low-bit guesses.

The official xoroshiro128++ 1.0 scrambler is

\[
y=\operatorname{ROTL}_{64}(a+b,17)+a\pmod{2^{64}}.
\]

Put \(c=a+b\). For a candidate second state word \(b\),

\[
z=y+b=c+\operatorname{ROTL}_{64}(c,17)\pmod{2^{64}}.
\]

**Exact inverse of the rotational sum.** Split \(c=2^{47}h+\ell\) with \(0\leq h<2^{17}\) and \(0\leq\ell<2^{47}\). Then

\[
\operatorname{ROTL}_{64}(c,17)=2^{17}\ell+h,
\]

so with \(A=2^{47}+1\), \(B=2^{17}+1=131073\), and \(M=2^{64}\),

\[
z+kM=Ah+B\ell,\qquad k\in\{0,1\}.
\]

The right side ranges from zero through \(2^{65}-2\); hence there is no unexamined wrap count. Since \(\gcd(A,B)=3\) and \(M\equiv 1\pmod3\), exactly one \(k\in\{0,1\}\) can satisfy divisibility by 3, and none does when \(z\bmod3=1\). For the admissible k,

\[
h\equiv \frac{(z+kM)\bmod B}{3}\cdot34956
       \pmod{43691},
\]

because \(B/3=43691\) and \(34956=(A/3)^{-1}\bmod43691\). There are at most **three** \(h\in[0,2^{17})\) in this residue class. For each, calculate

\[
\ell\equiv (z-Ah)\,B^{-1}\pmod{2^{64}},
\]

where \(B^{-1}\bmod2^{64}=\texttt{0xfff80003fffe0001}\). Retain only \(\ell<2^{47}\), reconstruct c and check \(c+\operatorname{ROTL}(c,17)\equiv z\). **No branch is heuristic:** these steps enumerate every exact solution of the original rotational-sum equation and no others. Recover the first state word \(a=c-b\pmod{2^{64}}\), then replay exact generator outputs.

### Scope and controls

- A separate local pure-math implementation recovered the planted c on **1,000,000 / 1,000,000** deterministic test inputs, observing at most three solutions per z; tests check the original modular equation, not just the modular residue.
- C++ [source-pinned half-state donor implementation](../agents/agent12/k04_xoropp_halfstate_donor_sft.cpp) independently plants a complete 128-bit state, applies the exact inversion and recovers the **whole six-word output stream** uniquely for that planted fixture. No selected physical coupon is used.
- An archive-sourced 16-byte-carrier test makes 556 distinct second-state-word proposals from **139 safe 16-byte original carriers** (131 nonselected printer payloads, two route fields, and six accepted components), under both half-word and byte directions. Across four independent layouts, 2,224 b-word proposals generated 1,972 exact first-output rotational roots, **zero states matching both words of the intact PS-0417 REQUESTED1 packet**. This excludes only those selected state-word donors, not xoroshiro128++ in general or an arbitrary initial state.
- The independent [PTW-417 signed seal serial search](../agents/agent12/k04_xoropp_ptw32_sft.cpp) fixes the source-selected highest signed CLOSED / AS_LEFT bay-A revision-2 seal serial as one 32-bit half of b and enumerates every value of the other 32 bits. Its original **4 × 2^32 = 17,179,869,184 complete b assignments** across all four packet byte-layout views yielded **zero** first-pair state fits and therefore zero original K04 commitment hits. The planted state with a nonzero unknown 24-bit half was recovered exactly once from a full \(2^{24}\)-element synthetic control. The 18:02 selected ACK2 copy was never decoded. The intact 18:03 REQUESTED3 was reserved for replay only.
- The [four-bay, two-position, two-serial-endian extension](../agents/agent12/k04_xoropp_ptw_allbay_sft.cpp) is deliberately distinct from the directly selected bay-A low-half model. Its additional original outcomes must be reported separately; do not assume they are complete merely because this reproducer is committed.

## Original-source and provenance boundary

All source-candidate constructions are **conjectural**: no original printer producer record states xoroshiro128++ was used, that successive REQUESTED / ACK / REQUESTED events consumed six consecutive outputs, or that any seal serial was an initial state word. The archived dispatch ACK is not a physical-coupon integrity witness. The target is tested only *after* a complete source-pair state fit; no full component from these models has passed the original K04 SHA-256 commitment.

The signed seal source is SHA256 \`c00944558636fbcc7e91b81e8e838ffd13fcd5a30d121b41951888766a8a0e32\`, printer source \`7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083\`, route \`f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5\`, and acceptance \`681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f\`. The program reads no PDF and checks the pinned hashes; source and verifier remain read-only. No public source-bearing CI was dispatched.

**What changes:** a precisely defined \(2^{64}\) state-word search is now a constant-work inverse *per proposed state word*, and half-word source-anchor hypotheses can be exhaustively evaluated on ordinary local compute without the previous SAT/UNKNOWN bottleneck. **What does not change:** the existence of a historical seal-to-printer connection, the true selected physical K04 coupon, and the missing K08 final wording remain unresolved; REC8/1 combined acceptance is still incomplete.
