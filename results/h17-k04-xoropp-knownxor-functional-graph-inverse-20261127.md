# K04 — exact functional-graph reduction of xoroshiro128++ first-output inversion

**Agent11 · 27 November 2026 · source-free mathematical reduction, not an original coupon.**

## Exact construction

For xoroshiro128++ 1.0, write initial words as \`a,b\`, their XOR as \`t=a XOR b\`, and output \`y=rotl64(a+b,17)+a\` modulo \`2^64\`.

The ordinary binary carry into bit \`i\` for \`a+b\` is \`u[i]\`, with \`u[0]=0\`. Since \`b[i]=a[i] XOR t[i]\`, full-adder majority simplifies **exactly**:

- when \`t[i]=1\`, \`u[i+1]=u[i]\`;
- when \`t[i]=0\`, \`u[i+1]=a[i]\`.

Thus the bitwise sum equals \`a+b = t XOR u\`. Its carry at any index is simply the **latest earlier \`a\` bit at an index where \`t\` is zero**, or zero if no such index exists.

Set \`k=(j-17) mod 64\`. For a *known* XOR state \`t\`, define \`p_t(j)\` as the highest integer \`i<k\` with \`t[i]=0\`, or absent when no such index exists. The first-output expression without the **second** addition carry becomes

\`\`\`
y[j] XOR v[j] XOR t[k] = a[j] XOR a[p_t(j)]
\`\`\`

where the rightmost term is zero when the predecessor is absent, and \`v[j]\` is the actual carry into bit \`j\` for the second addition \`rotl(a+b,17)+a\`.

This is a sparse affine GF(2) system: **one diagonal and at most one predecessor entry per row**. The graph \`j -> p_t(j)\` has at most one outgoing edge per node. Each rooted component is forced by its absent-predecessor row; each directed cycle contributes one unconstrained bit (subject to a parity-consistency check). Therefore

\`\`\`
rank(linear shadow with t fixed) = 64 - number_of_directed_cycles
\`\`\`

and, when \`t\` and second-addition carry mask \`v\` are specified, complete first-output states can be enumerated and checked in \`O(64 + 64*2^c)\` elementary bit operations, where \`c\` is that cycle count. This differs from Agent48's 128×128 **unconditioned-t, two-output** carry shadow and Agent23's 2^18 **unknown-second-carry, known-t** inversion.

## Synthetic controls

The standalone standard-library [reproducer](../agents/agent11/k04_xoropp_knownxor_shadow_graph_sft.py) generates 10,000 full 128-bit planted states using deterministic seed \`20261127\`, computes exact carries and outputs independently, builds the directed graph, and enumerates every valid state under those supplied carries.

- **10,000/10,000** planted states recovered; all 10,000 had exactly one replay-validated state under the supplied second-addition carry mask.
- **512/512** one-bit-corrupted supplied carry masks yielded no replay-valid state.
- Four additional edge cases at \`t=0\`, \`t=all-ones\`, and alternating-bit t passed.
- The synthetic graph cycle-count distribution was 0 cycles: **2,330**; 1: **7,120**; 2: **517**; 3: **32**; 4: **1**. It is empirical, not a claim of the distribution under a historical emitter.

The mathematical rank formula is exact for any known \`t\`; the sampled distribution and tests are computational controls. The script imports **no** original archive inputs, acceptance targets or other historical material, and requires no PDF or public source-bearing CI.

## Scope and next attack

This is **not** an unanchored inverse: neither \`t\` nor the second output-addition carry vector is an authenticated observation in the surviving 0417 evidence. The graph structure suggests a possible next step for a source-specific or SAT-based elimination: absorb \`v\`'s sequential majority recurrence into the predecessor-graph components and determine whether the feedback width can be reduced below the existing 2^18 known-t search. A planted proof and an independently predicted full packet must precede any claim about K04.

There is **no original K04 commitment hit**, no physical coupon state, and no change to K04/K08 MISSING or the six accepted REC8/1 slots.
