# K04: six-geometry joint CLASS/DEST uniform-publisher test

**Agent 30 | 9 November 2026 | Source-only original-archive experiment | 72 complete writer classes rejected.** No original K04 coupon was recovered.

## Recovery mechanism tested

The original print spool records two categorical labels, three CLASS values and three DEST values. A plausible compact printer issuer might generate the *joint* nine-way label using one random numeric draw, with an unknown fixed permutation assigning nine numeric buckets to the nine printed CLASS/DEST combinations. If that mechanism predicted intact original metadata, it could provide a source-constrained relation to the selected K04 coupon. The preceding integer rejection-sampler and packet-peek studies did not exhaust these **joint floating-point or scaled full-word issuers**.

Two source-producing transformations were frozen:

1. **53-bit two-word float:** two consecutive MT19937 tempered 32-bit values `a,b` produce `r=((a>>5)*2**26)+(b>>6)`, with category `floor(9*r/2**53)`. This is the actual standard CPython 53-bit random-float composition, with a nine-way category assignment hypothesized here.
2. **One-word scaled unsigned integer:** one 32-bit tempered value `a` gives category `floor(9*a/2**32)`. Unlike `randbelow(9)`, it consumes no rejection draws.

For each publisher, permit the category draw at the **first**, **last**, or **any** eligible native source position between two intact ordinary printer payloads. Associate each draw with either the **previous** or **following** original record's joint CLASS/DEST label. A static one-to-one nine-category codebook is unknown and fitted, rather than guessed from printable names.

Evaluate all six previously published, conditional, original-printer-compatible MT19937 start-index geometries p950..955. **The full selected row129 PS-261003-0417 ACK2 payload is excluded from state inference.** The original printer file SHA256 is `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. The exact source-only GF(2) ranks are 15366, 15365, 15367, 15368, 15365 and 15369 respectively.

Unknown projected MT output bits are treated *optimistically*: the potential numeric category is the full interval from setting all unresolved bits low to setting them high, then taking the nine-way floor. This may admit impossible joint completions, but never removes an actually compatible completion. Any incompatibility is therefore conservative, conditional on the chosen MT chronology.

## Original outcome

Across 6 chronology models × 2 publishers × 3 positions × 2 record-label bindings = **72 specific complete writer configurations**:

- **71 fail their first 95 original ordinary-record label transitions** even with arbitrary nine-way codebook and optimistic unknown-bit completions. Most have one or more original CLASS/DEST categories whose code domains are completely empty.
- **One source-trained survivor** uses chronology p953, the **single 32-bit scaled-word** publisher, **any** gap position and **previous-row** label binding. Exactly **62 complete codebooks** survive the first 95 records.
- **The untouched 32 later original label transitions reject that survivor.** The best training-compatible codebook predicts at most **30/32**. Under that best codebook the two direct failures are original gap rows **108** and **117**, both labeled LABEL/bench: its learned numeric code 5 is outside the allowed intervals `{0,2}` and `{0,1}` respectively. The full 127-gap domain has no possible one-to-one nine-way mapping.
- An independently frozen, source-class pair certificate under p951 with the two-word float at **any** gap position and previous-row binding: original LABEL/bench gap row21 permits numeric buckets `{0,1,2,3,4,5}`, while the same printed label at gap row22 permits **only bucket 8**. The sets are disjoint under even the optimistic source-bit projections.
- **128 actual Python-seeded synthetic two-word float computations and 128 one-word scaled computations** reproduce their exact nine-category result through the same GF(2) projection code. Planted tests are implementation checks; no synthetic target passes are called historical recovery.

Original source, acceptance, route mask, verifier, canonical six-PASS candidate and selected ACK2 copied bytes are unchanged. No K04 commitment was consulted to fit these models.

## Reproduce and next decision

[Read-only complete source SFT](../agents/agent30/k04_mt_joint_float_sft.py) reads either the original ZIP as its sole argument or the repo `resources/` by default. It emits one line per configuration and asserts that all 72 are source-incompatible. The model vectors are exact losslessly encoded deltas of the published [six cross-source stage vectors](https://github.com/FlareZ123/workplace-v1/blob/main/agents/agent5/k04_crosssource_six_vectors.json).

These exclusions apply **only** to the stated fixed nine-category issuers under the six historically unverified p950..955 MT geometries. They do not prove a different source emitter, reveal authentic original selected K04 coupon bits, or identify the final K08 text. A future target-reaching publisher needs **new source-defined, independently blind whole-object controls** or an additional source-indexed printed-media witness; adding a new arbitrary codebook to the incompatible joint-float model cannot repair the exact source contradictions.

**REC8/1 stays six individual PASS, K04/K08 unresolved, combined INCOMPLETE.**
