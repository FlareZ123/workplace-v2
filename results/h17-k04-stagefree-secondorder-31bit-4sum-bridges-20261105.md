# K04: stage-free second-order 31-bit MT four-sum bridges

**Agent 1 | 5 November 2026 | original-source-only result.** New recurrence-elimination mechanism and source-blinded packet graph refinement; original K04/K08 remain missing. An entirely new 4-source-word signature finds **15 exact 31-bit numerical matches** in the 132 intact original printer packets, with **nine lane-reinforced witnesses** grouped into four stage-difference tuples. One of these four reinforced groups creates three previously absent graph joins. The graph has **80 components instead of 83**, while the selected missing event still admits stages **917..971** under minimum monotonic chronology. This adds independent constraints on hypothetical native MT stage assignment, **zero authenticated target coupon bits**.

## Distinct algebraic mechanism

Agent13's earlier [stage-free 31bit triples](h17-k04-stagefree-31bit-hidden-predecessor-bridges-20261105.md) use one native MT19937 twist recurrence. Here eliminate the *unobserved middle output* between **two** twist recurrences. Writing untempered state outputs as `x[t]`:

```text
x[t+624] = x[t+397] XOR F(x[t], x[t+1])
x[t+397] = x[t+170] XOR F(x[t-227], x[t-226])
F(a,b) = (((a & 0x80000000) | (b & 0x7fffffff)) >> 1) XOR
          ((b & 1) * 0x9908b0df)
```

Only the MSB of each unobserved first argument influences bit 30 of `F`. With `L(b)=((b & 0x7fffffff)>>1) XOR ((b&1)*0x9908b0df)`, the **31-bit** identity is:

```text
(L(x[t-226]) XOR L(x[t+1])) & 0xbfffffff
  == (x[t+170] XOR x[t+624]) & 0xbfffffff
```

The four observed words therefore have exact relative stage offsets **0, 227, 396, 850**, unlike the previous three-output identity. A 31-bit pair-key hash enables a cheap complete scan of chronologically ordered four-word source combinations, with four-draw minimum chronology bounds. The inherited `STAGES` array plays **no role** in discovering matches or imposing original graph constraints.

## Original evidence, complete search and collision filtering

Source: unmodified `evidence/print/spool-reconstruction.log`, SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. The disputed selected 18:02 `PS-261003-0417` ACK2 row129 is withheld **before decoding its payload**. The remaining 132 original 16-byte buffers untemper into 528 native 32-bit source words.

The complete source scan yields **15 quartet assignments** partitioned into **10 (row tuple, three exact stage differences) groups**. Four groups contain independently shifted adjacent-lane identities, nine complete matches total:

| Four original packet rows | Implied packet start differences, relative to first row | Distinct observed 31-bit identities | Additional graph joins over Agent13 triples |
| --- | --- | ---: | ---: |
| 9, 40, 63, 124 | +229, +398, +852 | 2 | **3** |
| 10, 41, 64, 125 | +227, +397, +850 | 3 | 0 (previously connected) |
| 12, 43, 66, 128 | +229, +396, +852 | 2 | 0 (previously connected) |
| 13, 44, 67, 131 | +227, +395, +851 | 2 | 0 (previously connected) |

Six singleton identities require caution: original rows **4,35,58,118** and **5,36,59,119** have stage offsets inconsistent with the previously hypothesized p951 chronology. Treating numerical singletons as authoritative would create accidental source-graph claims. The source-first **lane-reinforcement** criterion was therefore imposed uniformly, leaving four groups. All nine repeated original identities retrospectively agree with p951, but that correspondence is **conditional**, without establishing historical generator or absolute timeline.

The previous first-order 42-relation weighted stage graph has 83 components and selected start range 917..971. Add the four reinforced second-order groups as exact interpacket difference constraints. Weighted union-find and Bellman-Ford with monotonic four-draw packet order report **80 components** and **unchanged 917..971** selected start bounds. In particular, original rows 9,40,63,124 become one new component. Neither selected neighbor is joined to the other, and no physical/copy-stage evidence appears.

## Planted producer and random-negative controls

The [portable single-file reproducible test](../agents/agent1/k04_mt_secondorder_4sum_sft.py) performs the source scan, reconstructs the 42 triple relations from scratch, applies the four reinforced new quartet constraints, verifies component counts/range, and runs four genuine Python `Random` MT histories at held-back reference stages: seeds `0`, `1`, `0x12345678`, `0xDEADBEEF`. Each synthetic history exhibits all nine true lane-reinforced identities in four groups; incidental singleton matches vary (total observed 14,14,13,17). Three unrelated pseudorandom 528-word negatives have respectively 3,1,0 singleton matches, **zero repeated groups**. The SFT was run locally against the original user-supplied 46-member ZIP and all assertions passed.

These empirical controls show reinforcement reduces accidental false numerical matches for this source length; they do not establish a probabilistic cryptographic certificate or historical writer provenance. A genuine planted complete producer does not predict the selected event while stage ambiguity persists.

## Outcome and useful next experiment

This is a new **source-structural relation**, not another seed or original-commitment brute sweep. It demonstrates a recurrence identity capable of connecting previously disconnected source graph components that single-twist triple tests cannot connect. A next test could derive distinct higher-order independent native relations or supply external indexed donor words to connect the two separate selected-neighbor components; any proposed connection must survive the repeated-lane controls before it is treated as genuine.

**REC8 remains six individually accepted components, K04/K08 missing, combined INCOMPLETE. No source, acceptance, mask, original candidate or verifier was altered.**
