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


## Stronger exact rotation-boundary first-output inverse (Agent11 continuation)

The functional graph also permits a **substantially faster unknown-carry inversion** when the initial state XOR word \`t\` and one output \`y0\` are given. Unlike the graph method above, this does **not** assume that the second-addition carry mask is known.

For first-output bit \`j\`, put \`k=(j-17) mod 64\` and \`q[j]=t[k] XOR u[k]\`, where \`u[k]\` is the first-adder carry. The bit equations for the second addition are

\`\`\`
a[j] = y0[j] XOR q[j] XOR v[j]
v[j+1] = (q[j] AND v[j]) if y0[j]=1
         (q[j] OR  v[j]) if y0[j]=0
v[0] = 0
\`\`\`

The carry recurrence follows directly by substituting \`a[j]\` into the binary full-adder majority function; it is an exact Boolean identity.

For \`j=0..16\`, \`k=j+47\`, so \`q[j]\` depends only on the state bits at the distinct *latest-zero-of-t* predecessor indices below 47..63. Let their number be \`D\`, at most 17. Enumerate only these **D unique predecessor bits**. Given one assignment, propagate \`a[j],v[j]\` from 0 through 63 using the equations above. For \`j>=17\`, \`k=j-17<j\`; therefore any predecessor of \`k\` was already reconstructed and requires **no additional guess**. Finally reject assignments inconsistent with their reconstructed predecessor bits and replay the exact 64-bit original output.

This enumerates **every** first-output state compatible with \`y0\` and the proposed \`t\`: the genuine predecessor assignment must appear in the enumeration, and each propagation step is forced. The complexity is \`O(64*2^D)\` versus Agent23's previous \`2^18\` low-\`a\`/carry hypotheses per proposed \`t\`. The bound is at most \`2^17\` assignments and normally much lower; it is not an unanchored 64-bit-\`t\` inversion.

### Independent controls and measured speed

The source-free [C++ exact inverter](../agents/agent11/k04_xoropp_knownxor_boundary_sft.cpp) independently checks the first-output roots against Agent23's earlier complete \`2^18\` inversion for 64 planted instances, then validates forward replay at both outputs. On a fixed-seed **100,000-state** synthetic experiment (seed \`20261127\`):

- 100,000 / 100,000 complete planted states recovered.
- 132,043,516 total boundary assignments, or **1,320.44 per known-\`t\` input on average**, versus 262,144 each for the old fixed-width enumeration: approximately **198.5× fewer assignments** across this trial.
- 117,588 total valid first-output roots; precisely 100,000 matched the second planted output.
- 64/64 independent exhaustive reference comparisons agreed on both the number of first-output roots and pair-output roots.
- Measured C++ wall time **26.96 seconds** for 100,000 cases, including the 64 reference exhaustions, on one local CPU. These timings are hardware- and fixture-dependent.

The random-fixture \`D\` distribution was concentrated around **9**, not 17; the full histogram is emitted by the reproducer. This is a method upgrade, not a new observation that xoroshiro actually produced the original printer record. The same historical packet, output-placement and authenticity caveats apply; **zero original K04 coupon outputs are claimed from the synthetic experiment**.

**Next decisive use:** Take only source-defensible candidate XOR-state words, invert the intact PS-0417 REQUESTED1 output pair using the faster algorithm, and replay all intact REQUESTED3 outputs *before* evaluating any selected physical coupon candidate against the unchanged K04 commitment. A match must still establish the historical producer relation; arbitrary donor lists do not.


## Original, bounded opaque-source XOR-state screen (read-only local test)

The new fast inverter enables a complete small-scale **source-linked \`t\` hypothesis** test that was impractical with the old fixed \`2^18\` method.

The original non-PDF \`resources/evidence\` tree contains **41 permitted evidence files**. An original spool SHA-256 gate was checked before use. The disputed selected \`PS-261003-0417\` 18:02 ACK2 row was **removed from all donor input** and never used as an output constraint. The exact 18:01 REQUESTED1 and 18:03 REQUESTED3 source packets were reserved for independent complete 64-bit output replay, with four predeclared 8-byte pair serializers (BE/LE and word-order swap).

From **opaque byte carriers only**, generate a proposed initial state XOR \`t\` as either (a) any 8-byte window in a source hex-decoded binary field or genuine raw recorder stream, interpreted both byte orders, or (b) XOR of the two 8-byte halves of any 16-byte such window, also in both byte orders. ASCII prose substrings and PDF bytes were not eligible donors. This produced 6,638 direct words and 4,494 two-half XOR words, **11,132 distinct proposed 64-bit t values**.

All **44,528** proposed \`t × serializer\` models were fully enumerated for first-output preimages using the new inverse. Exactly 44,670 first-output roots arose across serializers. **Zero** roots reproduced even the intact second 64-bit REQUESTED1 output, so none reached the held-out REQUESTED3 four-output gate or produced a physical K04 coupon candidate. No original commitment check was reached or claimed.

This excludes **only** the exact source-byte-donor/XOR-state construction and four packet serializers; it does not falsify the xoroshiro128++ producer class or prove the source rows independently intact. The complete-candidate first-pair replay is a sharp negative before the damaged/copied middle packet. Source-sensitive scanning was local, not run in public Actions. The original verifier, evidence, canonical candidate, and accepted six components were unchanged. K04/K08 remain MISSING; combined INCOMPLETE.


### Closed-form boundary-width distribution (mathematical, not empirical)

The number of independent guessed boundary bits admits a *closed-form* expression under a uniform random 64-bit proposed XOR word \`t\`:

\`\`\`
D(t) = 1{at least one zero in t[0..46]} + number_of_zeros(t[47..62]).
\`\`\`

This follows because only predecessor indices \`p_t(k)\` for \`k=47..63\` contribute; the first predecessor (if one exists before bit47) is one shared unknown, and each additional zero among bit positions47..62 first becomes the latest predecessor at the next boundary step. Bit63 never enters this boundary preimage list.

Consequently, with uniform independent \`t\` bits, \`Z ~ Binomial(16, 1/2)\`, and \`D=Z+B\` where \`B~Bernoulli(1-2^-47)\` is independent of Z. The *exact expected number of enumeration assignments* per known-\`t\` input is

\`\`\`
E[2^D] = (2 - 2^-47) (3/2)^16 ≈ 1,313.68167,
\`\`\`

compared with a fixed 262,144 for the previous \`2^18\` enumeration: an expected **199.55×** assignment reduction under a uniform random \`t\`. This is a distributional theorem for the algorithm, not an assumption about real printer state or proof of recoverability without \`t\`. At most 131,072 assignments are needed for any \`t\`; sparse t can approach that worst case.
