# K04: complete CPython two-word seed exclusion at genuine startup offset2493 by exact high-bit-guess/low-bit lifting

**Agent23 | 6 November 2026.** A genuinely new, fully exhausted 64-bit integer-seed necessary-condition screen for the original 132 preserved printer packets. K04 selected physical coupon remains unauthenticated, K08 final caption unknown, original combined REC8/1 six PASS and two MISSING. This source-only result is independent of the previously completed [k2492 direct inversion](h17-k04-cpython-k2492-two-word-complete-exclusion-20261106.md).

## Why offset2493 needs a different inversion

Under the conditional p951 printer fourword MT19937 schedule, original print log \`resources/evidence/print/spool-reconstruction.log\` SHA256 \`7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083\`, the **132 intact** rows generate rank15,365 original native-state equations with the disputed selected row129 withheld from fitting.

At true CPython initialized-register startup offset2493, independently compute these exact original source constraints:

| Word | Bit mask | Fixed value |
| --- | --- | --- |
| S2 | 8000001F | 00000011 |
| S3 | FFFFFFFF | E403BB7D |
| S4 | FFFFFFFF | 1F7B301F |
| S5 | 09CC1C00 | 008C1000 |
| S12 | 000000FF | 000000B6 |
| S13 | 5398BA7D | 4010A820 |

The second-pass CPython initialization identity forces the **entire firstpass A4** as \`(S4+4) XOR F2(S3) = 2AED5295\`, where \`F2(x)=1566083941*(x XOR (x>>30)) mod 2^32\`.

For a genuine two-word integer seed \`(k0,k1)\`, the firstpass \`init_by_array\` sequence is

\`\`\`text
A1 = (G1 XOR F1(G0)) + k0
A2 = (G2 XOR F1(A1)) + k1 + 1
A3 = (G3 XOR F1(A2)) + k0
A4 = (G4 XOR F1(A3)) + k1 + 1
F1(x) = 1664525 * (x XOR (x>>30)) mod 2^32
\`\`\`

The full A4 constraint is nonlinear in both seed words, so the earlier k2492 direct method cannot solve k1 immediately. Here the original S5 nine-bit mask, combined with known original S4, gives a **seed-k0-only prefilter**: compute firstpass \`A5=(G5 XOR F1(A4))+k0\`, then \`S5=(A5 XOR F2(S4))-5\`. This reduces the entire 2^32 k0 search to 8,388,608, with **no assumption on k1**.

## Exact bitwise inverse, covering every possible k1

For each surviving k0, enumerate the two high-bit patterns of the unknown firstpass **A2** and **A3**. There are precisely 4×4 possibilities. Denote these \`h2=A2>>30\` and \`h3=A3>>30\`, each 0..3. Under each guessed pair, the transformations \`F1(A2)=1664525*(A2 XOR h2)\` and \`F1(A3)=1664525*(A3 XOR h3)\` become **triangular over successive low-order bits**: their output modulo 2^b depends only on the input modulo 2^b, plus the already frozen high-two-bit patterns.

Start with a zero-bit partial k1. For each bit 0..31, extend every surviving low-bit prefix by both possible next bits, keeping only prefixes whose derived A4 matches the original 2AED5295 through that bit. Never cap the candidate branch list; the largest observed list per prefix has 232 members. For every final 32-bit root, explicitly recompute genuine high-two-bit A2/A3 and discard mismatched guesses. This proves **completeness over all 2^64 two-word integers**: every real candidate's exact k0 is visited, its two actual high-two-bit patterns are enumerated, and its low-bit prefixes survive every exact necessary congruence.

Recover the required second-pass S2 from original S3 and firstpass A3 by inverting F2:

\`\`\`text
z = 6A76AE6D * (A3 XOR (S3+3)) mod 2^32
S2 = z XOR (z>>30)
\`\`\`

The multiplier \`6A76AE6D\` is the inverse of 1566083941 mod 2^32. Require the original S2 6-bit mask and propagate full actual first and second \`init_by_array\` words through S13; test independently preserved S12 and S13 original masks. No selected original ACK bytes or K04 commitment enter any step.

## Full original enumeration and independent seeded controls

Executed local source-pinned C++17/OpenMP complete 2^32 k0 domain with the odd multiplier \`0x9E3779B9\` used solely to permute the scanning order and spread a short pilot across the domain. The final exhaustive pass consumed all 2^32 k0 values exactly once, 16 high-bit geometry assignments per prefiltered k0, and every full low-bit root under each geometry:

| Exact source test | Surviving assignments |
| --- | ---: |
| k0 entire domain | 4,294,967,296 |
| Original S5 nine-bit k0 prefilter | 8,388,608 |
| All high-two-bit pair geometries | 134,217,728 |
| Full low-bit lifted roots, before removing inconsistent high-bit guesses | 184,552,152 |
| Exact actual A2/A3 high-two-bit checks | 11,546,079 |
| Original S2 mask | 168,980 |
| Original S12 mask | 662 |
| Original S13 mask | **0** |

Source execution summary:

\`\`\`text
K2493_N2_LIMIT=4294967296 PREFILTER=8388608 PATHS=134217728 ROOTS=184552152 HIGHBITS=11546079 S2=168980 S12=662 S13=0 MAXBRANCH=232
\`\`\`

A disjoint numerical pilot sampling 1,048,576 k0 through the same odd-multiplier domain permutation yielded 2,019 prefiltered values, 2,932 high-bit consistent roots, 32 original S2-compatible roots and zero S12. This pilot did not determine final counts; the full run did.

The **five genuine CPython two-word seed positive controls** include \`(12345678,23456789)\`, \`(1,1)\`, \`(FFFFFFFF,FFFFFFFF)\`, \`(00001FC3,00001092)\`, and \`(0,80000000)\`. For each, independently construct \`random.Random((k1<<32)|k0).getstate()\` and derive its own A4. The full 32-bit bit-lift using the seed's authentic two high-bit patterns must retain the planted k1 at **every one of 32 bit extensions**. It does in all five cases. Additional source-stage checks recover actual seeded S2 from A3/S3 and exactly reproduce actual seeded S5..S13. **5/5 pass**.

Reproducer [source-pinned single runnable original SFT](../agents/agent23/k04_cpython_k2493_n2_bitlift_sft.py) recomputes original S2/S3/S4/S5/S12/S13 source observations using the prior independently tested Agent28 projector with selected row129 omitted, exercises the five planted positives, compiles an embedded C++17/OpenMP enumerator and asserts all original full-domain counts. The standalone equivalent C++ file was compiled and executed on the original supplied ZIP extraction locally.

## Consequence and scope

The result **fully excludes every genuine two-32-bit-word CPython integer seed at real prior-output offset2493**, under the conditionally chosen p951 native printer chronology and byte ordering. Combined with the independent k2492 result, it closes genuine n2 seeds at those **two specific offsets**. It does not establish that the historical printer actually used CPython, the selected fourword target came from this hypothetical stream, or that any other startup offset fails. It leaves the physical original K04 coupon entirely unknown and does not recover K08's literal final caption.

The key reusable research method is **high-output-bit pattern enumeration followed by 2-adic low-bit lifting**, where a nontriangular \`x XOR (x>>30)\` word function becomes triangular after its two high input bits are guessed. This permits exact complete seed-domain screens without generic SMT timeouts and may be reusable if a documented source/producer phase makes other early register constraints worth attacking. Further blind phase sweeps without source-selection evidence remain low priority. All archival sources, acceptance commitments, official verifier and canonical candidate were unchanged.
