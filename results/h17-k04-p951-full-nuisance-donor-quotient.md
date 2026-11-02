# K04 p951 full-state donor quotient: a single sensitive window supplies no complete-key information

**Agent 1 | 2 November 2026 | Computational theorem conditional on the speculative p951 shared-MT19937 chronology. No original K04 component is recovered.**

## Research question

[Agent 8's negative-time p951 frontier](h17-k04-p951-negative-causal-frontier.md) constructs 128 printer-compatible MT state perturbations that span all 128 selected K04 raw output bits. They affect 33 earlier state indices, assembled into eight groups. For example, the **five** indices -919..-915 have rank **127** when evaluated on that *particular 128-direction perturbation subspace*. Do original output observations throughout this window actually recover selected K04 bits after allowing every other printer-compatible MT state variable to adjust?

This distinction matters for pursuing PTW-417 and other cross-carrier serials as missing-state donors: a donor can intersect a selected-changing subspace yet still be completely compensated by omitted nuisance state variations. It was not addressed by the earlier 128-direction-only rank calculation.

## Exact source-only linear model

- Import the original 133 spool packets and the fixed [Agent 2 p951 chronology](../agents/agent2/20261102_k04_multicarrier_p951_sft.py), excluding **row129** from every state equation. Source SHA256: `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. The p951 chronology is a research hypothesis, not historical printer firmware evidence.
- Replicate Agent2's fixed-point propagation: **968 fully reconstructed and 306 partially reconstructed state words** from 528 intact 32-bit output words.
- Represent the 624 consecutive raw state words X[0..623] as 19,968 symbolic GF(2) bits. The source-fixed point leaves **6,202 initially unknown bit variables**. Explicitly impose all 528 original unselected tempered outputs and the 31-bit reverse-continuation boundary equation; their joint equations have rank **1,630** on these remaining variables. All are consistent.
- Extend the standard MT equation X[t+624] = X[t+397] XOR twist(X[t],X[t+1]) forward to +2259 and backward to -1100; implement invertible MT tempering symbolically. Synthetic native CPython MT control, with 3,500 actual generated words and the 624-word middle span, reproduces tested negative/positive raw words and all 31 boundary equations.
- Project all 128 selected tempered output bit expressions (X[951..954]) modulo the full original-source equation span: target rank is **128/128**, as expected. For a *hypothetical* original output at any donor index, augment the homogeneous equation space and measure **conditional target rank change**. Synthetic hypothetical donor values are used only for linear rank geometry, never promoted into source observations. The actual selected ACK, target commitment, route mask and verifier are not consulted.

### Results: whole 32-bit original donor words

| Hypothetical observed index group | Information gained on selected 128 bits after all nuisance variables are eliminated |
| --- | ---: |
| -1089..-1084 | 0 |
| -919..-915 | **0** |
| -861..-857 | 0 |
| -692 | 0 |
| -523 | 1 |
| -465..-461 | 0 |
| -296..-292 | 0 |
| -69..-65 | 0 |
| Joint **-919..-915, -465..-461, -296..-292** | **127** |
| Joint **all 33** negative positions | **127** |

The three separated five-word windows have a joint target residual rank of **one**, despite every individual five-word window supplying **zero** conditional selected-bit information. All 33 negative positions also leave that same residual bit. Under this very strong hypothetical observation set, any **one full native MT output** at positive index **+1179, +1349, +1406, +1633, +1803 or +2257** closes the last residual target dimension. These positive indices were tested against the full equation span through +2259, excluding the selected event; no such original outputs are observed.

This demonstrates a genuine *joint-observation synergy* that the single-window 128-direction rank cannot establish. The earlier rank-127 on chosen perturbations remains mathematically correct within its subspace; interpreting that rank as a 127-bit usable K04 recovery from one preserved PTW window would overstate the full model.

### Residual-bit shape and individual donor necessity

Under the hypothetical exact observation of the three rank-127 windows (-919..-915, -465..-461, -296..-292), the only remaining selected-output variation is one GF(2) direction with a **six-bit** coupon XOR delta, represented in selected packet byte order as `00000000042210880000000000000000` (little-endian word lanes `00000000, 88102204, 00000000, 00000000`). This is the **difference between two conditional candidates**, not a source-derived K04 component and not evidence that six physical copy bits are actually wrong. The exact same residual direction survives after granting all 33 negative-window words.

The three-window observation set contains 15 original-output words. Removing **any one** of those 15 reduces the calculated information gain below 127 bits (the range is 95–125, depending on the position). A tested 100-order greedy-removal pilot found the same irreducible 15-word set. Thus the rank-127 synergy has no redundant donor word in that specific combination; a single additional PTW receipt from one window cannot replace the other entire groups.

## Chronological PTW producer falsifier, limited scope

Under the same speculative p951 state, original serial anchors PTW-405 at -964, PTW-412 at -944 and PTW-414 at -937 match; the observed original bay C at PTW-414 matches a proposed immediately preceding `getrandbits(3)` code at -938. To test whether that is part of a *uniform producer*, a frozen source-only model emits **bay = CPython randrange(4), allowing 1..12 rejection draws, then serial = getrandbits(32)** in ascending permit order. The withheld PTW-415 bay A and serial can fit at serial indices -934 or -933. For **both**, the next PTW-416 bay D plus exact original serial has **no consistent 1..12-draw placement** in the full printer equation system. A reverse within-record serial/bay variant likewise has no such consistent PTW-416 placement.

This rejects only the explicit immediate two-field emission/order model and rejection limit, without proving that the historically shared PRNG, indexing, or record ordering is wrong. It demonstrates why a single retrospective PTW-414 bay agreement cannot certify a PTW417 donor timeline.

## Research consequence

Seeking one full source packet solely within the attractive -919..-915 PTW window would leave K04 wholly ambiguous **within this broader p951 generator model**. A promising line would instead identify a historically justified producer seed/epoch capable of eliminating the nuisance variables, or independently indexed original outputs in *multiple separated* windows with a prospective held-out check. The hypothetical three-window information gain shows that multiwindow source relationships can be materially different from another same-window source match.

The reproducible source-only SFT was executed locally with a 3,500-word synthetic CPython control. Its repository upload was blocked, so this report preserves the exact rank inputs, equations and output assertions; the executing agent retains the script in the current conversation's downloadable artifacts. No original evidence, accepted candidate, route, acceptance file or verifier is changed. Six established component checks PASS; K04 and K08 remain missing; combined REC8 remains INCOMPLETE.


## Smaller full-rank hypothetical donor configuration, 20:57 UTC

A follow-on greedy deletion across the 33 earlier sensitive positions and six mathematically qualified future positions finds a **15-fullword** source set reducing the selected 128-bit quotient to zero:

\`[-919,-918,-917,-916,-915,-523,-465,-464,-462,-461,-295,-293,-292,1349,1406]\`.

The construction first excludes selected row129, rebuilds all 6202 initial unknown state forms and 1630 independent original printer constraints, then iteratively drops donor indices only if \`rank([target; donors])-rank(donors)==0\` remains true. Among 120 deterministically seeded randomized deletion orders, the strongest kept 15 distinct complete 32-bit donor outputs, versus the earlier 16-word three-window-plus-future example. This is an **upper bound on the number of hypothetical donor outputs sufficient** in that source-model geometry, with no claim of global cardinality minimality or actual indexed source records at those 15 positions. It requires two separate positive-time outputs and several earlier windows. No authentic target value was supplied by this symbolic exercise.
